from __future__ import annotations

import re
from typing import Any

from .catalog import Catalog
from .exceptions import AmbiguousColumnError, ColumnNotFoundError, InvalidFilterError, RelationshipNotFoundError
from .models import Confidence, FilterCondition, RelationshipAuthority, RelationshipCandidate, SqlGenerationRequest, SqlGenerationResult
from .relationships import RelationshipEngine

SAFE_NAME = re.compile(r"^[A-Z][A-Z0-9_$#]*$")


class SQLGenerator:
    def __init__(self, catalog: Catalog, relationships: RelationshipEngine):
        self.catalog, self.relationships = catalog, relationships

    def generate(self, request: SqlGenerationRequest) -> SqlGenerationResult:
        tables = [self.catalog.get_table(t).name for t in request.tables]
        if len(tables) != len(set(tables)):
            raise ValueError("Tabelas duplicadas não são permitidas")
        aliases = self._aliases(tables)
        selected = request.columns or [f"{t}.{c.name}" for t in tables for c in self.catalog.get_table(t).columns]
        resolved = [self._resolve_column(c, tables) for c in selected]
        if request.grain is not None:
            grain = [self._resolve_column(column, tables) for column in request.grain]
            if any(table != tables[0] for table, _ in grain):
                raise RelationshipNotFoundError(
                    f"Grão declarado deve pertencer à tabela base {tables[0]} nesta validação mínima"
                )
        joins, used, warnings = self._joins(tables, request.allow_low_confidence, request.grain is not None)
        select_lines = [f"    {aliases[t]}.{c}" for t, c in resolved]
        sql = "SELECT\n" + ",\n".join(select_lines) + f"\nFROM {tables[0]} {aliases[tables[0]]}"
        connected = {tables[0]}
        for rel in joins:
            if rel.source_table in connected:
                old, new = rel.source_table, rel.target_table
            else:
                old, new = rel.target_table, rel.source_table
            if new == rel.target_table:
                new_columns, old_columns = rel.target_columns or [], rel.source_columns or []
            else:
                new_columns, old_columns = rel.source_columns or [], rel.target_columns or []
            predicates = [
                f"{aliases[new]}.{new_column} = {aliases[old]}.{old_column}"
                for new_column, old_column in zip(new_columns, old_columns)
            ]
            sql += f"\nLEFT JOIN {new} {aliases[new]}\n    ON " + "\n    AND ".join(predicates)
            connected.add(new)
        params: dict[str, Any] = {}
        clauses = []
        for index, condition in enumerate(request.filters or [], 1):
            table, column = self._resolve_filter(condition, tables)
            alias, operator = aliases[table], condition.operator
            if operator in {"IS NULL", "IS NOT NULL"}:
                if condition.value is not None:
                    raise InvalidFilterError(f"{operator} não aceita valor")
                clauses.append(f"{alias}.{column} {operator}")
            elif operator == "IN":
                if not isinstance(condition.value, (list, tuple)) or not condition.value:
                    raise InvalidFilterError("IN exige uma lista não vazia")
                names = []
                for offset, value in enumerate(condition.value, 1):
                    name = f"p{index}_{offset}"; params[name] = value; names.append(f":{name}")
                clauses.append(f"{alias}.{column} IN ({', '.join(names)})")
            else:
                if condition.value is None:
                    raise InvalidFilterError(f"{operator} exige valor")
                name = f"p{index}"; params[name] = condition.value
                clauses.append(f"{alias}.{column} {operator} :{name}")
        if clauses:
            sql += "\nWHERE " + "\n  AND ".join(clauses)
        return SqlGenerationResult(sql=sql, parameters=params, warnings=warnings, relationships=used)

    def _resolve_column(self, reference: str, tables: list[str]) -> tuple[str, str]:
        parts = reference.upper().split(".")
        if len(parts) == 2:
            table, column = parts
            if table not in tables: raise ColumnNotFoundError(f"Tabela da coluna não foi selecionada: {table}")
            if column not in {c.name for c in self.catalog.get_table(table).columns}: raise ColumnNotFoundError(f"Coluna inexistente: {reference}")
            return table, column
        if len(parts) != 1 or not SAFE_NAME.fullmatch(parts[0]): raise ColumnNotFoundError(f"Referência de coluna inválida: {reference}")
        matches = [(t, parts[0]) for t in tables if parts[0] in {c.name for c in self.catalog.get_table(t).columns}]
        if not matches: raise ColumnNotFoundError(f"Coluna inexistente nas tabelas selecionadas: {reference}")
        if len(matches) > 1: raise AmbiguousColumnError(f"Coluna ambígua {reference}; qualifique com TABELA.COLUNA")
        return matches[0]

    def _resolve_filter(self, condition: FilterCondition, tables: list[str]) -> tuple[str, str]:
        ref = f"{condition.table}.{condition.column}" if condition.table else condition.column
        try: return self._resolve_column(ref, tables)
        except (ColumnNotFoundError, AmbiguousColumnError) as exc: raise InvalidFilterError(str(exc)) from exc

    def _aliases(self, tables: list[str]) -> dict[str, str]:
        result, counts = {}, {}
        for table in tables:
            base = "".join(part[0] for part in table.replace("RAW_", "").split("_") if part)[:4].lower() or "t"
            counts[base] = counts.get(base, 0) + 1
            result[table] = base if counts[base] == 1 else f"{base}{counts[base]}"
        return result

    def _joins(self, tables: list[str], allow_low: bool, require_grain: bool = False) -> tuple[list[RelationshipCandidate], list[RelationshipCandidate], list[str]]:
        if len(tables) == 1: return [], [], []
        connected, pending, joins, warnings = {tables[0]}, set(tables[1:]), [], []
        while pending:
            choices = [r for r in self.relationships.candidates if (r.source_table in connected and r.target_table in pending) or (r.target_table in connected and r.source_table in pending)]
            if not choices: raise RelationshipNotFoundError(f"Não há relacionamento aceitável para conectar: {', '.join(sorted(pending))}")
            rel = max(choices, key=lambda r: r.score)
            self._require_approved_relationship(rel)
            if rel.confidence == Confidence.LOW and not allow_low:
                raise RelationshipNotFoundError(f"Não há relacionamento aceitável para conectar: {', '.join(sorted(pending))}")
            joins.append(rel)
            new = rel.target_table if rel.source_table in connected else rel.source_table
            old = rel.source_table if rel.source_table in connected else rel.target_table
            if require_grain:
                proof = self.relationships.grain_preservation(rel, old)
                if not proof["preserves_grain"]:
                    raise RelationshipNotFoundError(
                        f"Preservação de grão bloqueada em {old} → {new}: "
                        f"{'; '.join(proof['reasons'])}. Requer cardinalidade N:1/1:1 autorizada "
                        "e chave PRIMARY_KEY/UNIQUE correspondente no lado alcançado; "
                        "nenhuma deduplicação automática será aplicada."
                    )
            connected.add(new); pending.remove(new)
            if rel.confidence != Confidence.HIGH:
                warnings.append(
                    f"JOIN usa relacionamento candidato {rel.confidence}: "
                    f"{rel.source_table}.{','.join(rel.source_columns or [])} ↔ "
                    f"{rel.target_table}.{','.join(rel.target_columns or [])}"
                )
        return joins, joins, warnings

    @staticmethod
    def _require_approved_relationship(rel: RelationshipCandidate) -> None:
        endpoints = f"{rel.source_table}.{rel.source_column} ↔ {rel.target_table}.{rel.target_column}"
        reasons = []
        if rel.authority != RelationshipAuthority.APPROVED:
            authority = rel.authority.value if rel.authority is not None else "AUSENTE"
            reasons.append(f"autoridade {authority}")
        if rel.conflicts:
            reasons.append(f"conflito(s): {'; '.join(rel.conflicts)}")
        if reasons:
            raise RelationshipNotFoundError(
                f"Relacionamento bloqueado {endpoints}: {', '.join(reasons)}. "
                "A relação precisa de homologação como APPROVED e estar livre de conflitos."
            )

    def generate_select(self, table: str, columns: list[str] | None = None) -> SqlGenerationResult:
        return self.generate(SqlGenerationRequest(tables=[table], columns=columns))
