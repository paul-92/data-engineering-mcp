from __future__ import annotations

from collections import Counter, defaultdict, deque
import json
from pathlib import Path

from pydantic import ValidationError

from .catalog import Catalog
from .exceptions import PathNotFoundError, RelationshipNotFoundError
from .models import (
    Cardinality, Confidence, ExplicitKey, ExplicitRelationship, KeyConstraint,
    RelationshipCandidate, RelationshipMetadata, RelationshipPath,
)

GENERIC = {"ID", "CODIGO", "CD", "STATUS", "FL_STATUS", "DT_PROCESSAMENTO", "DT_ATUALIZACAO", "NU_SEQ"}


class RelationshipEngine:
    def __init__(self, catalog: Catalog, metadata_path: Path | None = None):
        self.catalog = catalog
        self.metadata_path = metadata_path
        self.candidates: list[RelationshipCandidate] = []
        self.keys: list[KeyConstraint] = []

    def infer(self) -> list[RelationshipCandidate]:
        occurrences: dict[str, list[str]] = defaultdict(list)
        for table in self.catalog.tables.values():
            for column in table.columns:
                occurrences[column.name].append(table.name)
        result: list[RelationshipCandidate] = []
        for column, tables in occurrences.items():
            if len(tables) < 2:
                continue
            for index, left in enumerate(sorted(tables)):
                for right in sorted(tables)[index + 1:]:
                    score, reasons = self._score(column, left, right, len(tables))
                    confidence = Confidence.HIGH if score >= 75 else Confidence.MEDIUM if score >= 50 else Confidence.LOW
                    result.append(RelationshipCandidate(source_table=left, source_column=column,
                        target_table=right, target_column=column, confidence=confidence, score=score,
                        rationale="; ".join(reasons) + "; relacionamento candidato, não confirmado"))
        metadata = self._load_explicit()
        self.keys = self._merge_keys(metadata.keys)
        self.candidates = self._merge_explicit(result, metadata.relationships)
        return self.candidates

    def _load_explicit(self) -> RelationshipMetadata:
        if self.metadata_path is None or not self.metadata_path.exists():
            return RelationshipMetadata(relationships=[])
        try:
            payload = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            return RelationshipMetadata.model_validate(payload)
        except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            raise ValueError(f"Metadado de relacionamentos inválido em {self.metadata_path}: {exc}") from exc

    def _merge_keys(self, explicit: list[ExplicitKey]) -> list[KeyConstraint]:
        grouped: dict[tuple[str, tuple[str, ...]], list[ExplicitKey]] = defaultdict(list)
        for key in explicit:
            self._validate_key(key)
            grouped[(key.table, tuple(key.columns))].append(key)
        merged = []
        for identity, entries in grouped.items():
            signatures = {(entry.kind, entry.source, entry.authority, str(entry.decision)) for entry in entries}
            conflicts = [] if len(signatures) == 1 else [f"entradas de chave incompatíveis para {identity}"]
            entry = sorted(entries, key=lambda item: (item.source, item.kind.value, item.authority.value))[0]
            merged.append(KeyConstraint(**entry.model_dump(), conflicts=conflicts))
        return sorted(merged, key=lambda key: (key.table, key.columns, key.kind.value, key.source))

    def _validate_key(self, key: ExplicitKey) -> None:
        table = self.catalog.get_table(key.table)
        available = {column.name for column in table.columns}
        missing = [column for column in key.columns if column not in available]
        if missing:
            raise ValueError(f"Metadado de relacionamentos inválido: coluna(s) de chave inexistente(s) {key.table}.{', '.join(missing)}")

    @staticmethod
    def _identity(rel: RelationshipCandidate | ExplicitRelationship) -> tuple[tuple[str, tuple[str, ...]], tuple[str, tuple[str, ...]]]:
        return tuple(sorted(((rel.source_table, tuple(rel.source_columns or [])), (rel.target_table, tuple(rel.target_columns or [])))))

    @staticmethod
    def _table_pair(rel: RelationshipCandidate | ExplicitRelationship) -> tuple[str, str]:
        return tuple(sorted((rel.source_table, rel.target_table)))

    def _merge_explicit(self, inferred: list[RelationshipCandidate], explicit: list[ExplicitRelationship]) -> list[RelationshipCandidate]:
        by_identity: dict[tuple[tuple[str, tuple[str, ...]], tuple[str, tuple[str, ...]]], list[ExplicitRelationship]] = defaultdict(list)
        for rel in explicit:
            by_identity[self._identity(rel)].append(rel)

        conflicts: dict[tuple[str, str], list[str]] = defaultdict(list)
        explicit_by_pair: dict[tuple[str, str], set[tuple[tuple[str, tuple[str, ...]], tuple[str, tuple[str, ...]]]]] = defaultdict(set)
        for identity, entries in by_identity.items():
            pair = self._table_pair(entries[0])
            explicit_by_pair[pair].add(identity)
            signatures = {(entry.authority, entry.source, str(entry.decision)) for entry in entries}
            if len(signatures) > 1:
                conflicts[pair].append(f"entradas explícitas incompatíveis para {identity}")
        for pair, identities in explicit_by_pair.items():
            if len(identities) > 1:
                conflicts[pair].append("fontes explícitas discordam sobre as colunas dos endpoints")
        inferred_by_pair: dict[tuple[str, str], set[tuple[tuple[str, tuple[str, ...]], tuple[str, tuple[str, ...]]]]] = defaultdict(set)
        for rel in inferred:
            inferred_by_pair[self._table_pair(rel)].add(self._identity(rel))
        for pair, explicit_id_set in explicit_by_pair.items():
            partial_inferences = {
                inferred_identity for inferred_identity in inferred_by_pair[pair]
                if any(
                    all(
                        inferred_endpoint[0] == explicit_endpoint[0]
                        and set(inferred_endpoint[1]).issubset(explicit_endpoint[1])
                        for inferred_endpoint, explicit_endpoint in zip(inferred_identity, explicit_identity)
                    )
                    for explicit_identity in explicit_id_set
                )
            }
            unexpected_inferences = inferred_by_pair[pair] - partial_inferences - explicit_id_set
            if unexpected_inferences:
                conflicts[pair].append("metadado explícito e inferência discordam sobre as colunas dos endpoints")

        merged: list[RelationshipCandidate] = []
        inferred_by_identity = {self._identity(rel): rel for rel in inferred}
        explicit_identities = set(by_identity)
        for identity, entries in by_identity.items():
            entry = sorted(entries, key=lambda item: (
                item.source, item.authority.value, item.cardinality.value,
                item.cardinality_source or "", item.cardinality_authority.value if item.cardinality_authority else "",
            ))[0]
            self._validate_endpoint(entry.source_table, entry.source_columns or [])
            self._validate_endpoint(entry.target_table, entry.target_columns or [])
            base = inferred_by_identity.get(identity)
            pair_conflicts = sorted(set(conflicts[self._table_pair(entry)]))
            cardinality_conflicts = self._cardinality_conflicts(entries)
            merged.append(RelationshipCandidate(
                source_table=entry.source_table,
                source_column=entry.source_column,
                source_columns=entry.source_columns,
                target_table=entry.target_table,
                target_column=entry.target_column,
                target_columns=entry.target_columns,
                confidence=base.confidence if base else Confidence.HIGH,
                score=base.score if base else 100,
                rationale=(base.rationale + "; metadado explícito prevalece" if base else "relacionamento declarado em metadado explícito"),
                authority=entry.authority,
                source=entry.source,
                decision=entry.decision,
                conflicts=pair_conflicts,
                cardinality=entry.cardinality,
                cardinality_source=entry.cardinality_source,
                cardinality_authority=entry.cardinality_authority,
                cardinality_decision=entry.cardinality_decision,
                cardinality_conflicts=cardinality_conflicts,
            ))
        for rel in inferred:
            if self._identity(rel) not in explicit_identities:
                pair_conflicts = sorted(set(conflicts[self._table_pair(rel)]))
                merged.append(rel.model_copy(update={"conflicts": pair_conflicts}))
        return sorted(merged, key=lambda r: (-r.score, r.source_table, r.target_table, tuple(r.source_columns or []), r.authority.value))

    @classmethod
    def _cardinality_conflicts(cls, entries: list[ExplicitRelationship]) -> list[str]:
        signatures = {
            (cls._canonical_cardinality(entry), entry.cardinality_source, entry.cardinality_authority, str(entry.cardinality_decision))
            for entry in entries
        }
        return [] if len(signatures) == 1 else ["entradas explícitas discordam sobre cardinalidade ou sua autoridade"]

    @classmethod
    def _canonical_cardinality(cls, rel: ExplicitRelationship) -> Cardinality:
        canonical_source = cls._identity(rel)[0]
        if (rel.source_table, tuple(rel.source_columns or [])) == canonical_source:
            return rel.cardinality
        inverse = {
            Cardinality.MANY_TO_ONE: Cardinality.ONE_TO_MANY,
            Cardinality.ONE_TO_MANY: Cardinality.MANY_TO_ONE,
        }
        return inverse.get(rel.cardinality, rel.cardinality)

    @staticmethod
    def oriented_cardinality(rel: RelationshipCandidate, from_table: str) -> Cardinality:
        from_table = from_table.upper()
        if from_table == rel.source_table:
            return rel.cardinality
        if from_table != rel.target_table:
            raise ValueError(f"Tabela {from_table} não participa do relacionamento")
        inverse = {
            Cardinality.MANY_TO_ONE: Cardinality.ONE_TO_MANY,
            Cardinality.ONE_TO_MANY: Cardinality.MANY_TO_ONE,
        }
        return inverse.get(rel.cardinality, rel.cardinality)

    def keys_for_table(self, table: str) -> list[KeyConstraint]:
        name = self.catalog.get_table(table).name
        return [key for key in self.keys if key.table == name]

    def matching_key(self, table: str, columns: list[str]) -> KeyConstraint | None:
        wanted = [column.upper() for column in columns]
        matches = [key for key in self.keys_for_table(table) if key.columns == wanted]
        return matches[0] if matches else None

    def grain_preservation(self, rel: RelationshipCandidate, from_table: str) -> dict:
        from_name = self.catalog.get_table(from_table).name
        if from_name == rel.source_table:
            target_table, target_columns = rel.target_table, list(rel.target_columns or [])
        elif from_name == rel.target_table:
            target_table, target_columns = rel.source_table, list(rel.source_columns or [])
        else:
            raise ValueError(f"Tabela {from_name} não participa do relacionamento")
        cardinality = self.oriented_cardinality(rel, from_name)
        key = self.matching_key(target_table, target_columns)
        reasons = []
        if cardinality not in {Cardinality.MANY_TO_ONE, Cardinality.ONE_TO_ONE}:
            reasons.append(f"cardinalidade {cardinality.value}")
        if rel.cardinality_authority is None:
            reasons.append("autoridade de cardinalidade AUSENTE")
        if rel.cardinality_conflicts:
            reasons.append(f"conflito(s) de cardinalidade: {'; '.join(rel.cardinality_conflicts)}")
        if key is None:
            reasons.append(f"unicidade não comprovada em {target_table}.{','.join(target_columns)}")
        elif key.conflicts:
            reasons.append(f"conflito(s) de chave: {'; '.join(key.conflicts)}")
        preserves = not reasons
        return {
            "from_table": from_name,
            "target_table": target_table,
            "cardinality": cardinality.value,
            "cardinality_authority": rel.cardinality_authority.value if rel.cardinality_authority else None,
            "cardinality_source": rel.cardinality_source,
            "cardinality_conflicts": rel.cardinality_conflicts,
            "target_key": key.model_dump(mode="json") if key else None,
            "preserves_grain": preserves,
            "status": "PRESERVES" if preserves else "BLOCKED",
            "reasons": reasons,
        }

    def _validate_endpoint(self, table_name: str, column_names: list[str]) -> None:
        table = self.catalog.get_table(table_name)
        available = {column.name for column in table.columns}
        missing = [column for column in column_names if column not in available]
        if missing:
            raise ValueError(f"Metadado de relacionamentos inválido: coluna(s) inexistente(s) {table_name}.{', '.join(missing)}")

    def _score(self, column: str, left: str, right: str, frequency: int) -> tuple[int, list[str]]:
        score, reasons = 20, ["mesmo nome de coluna"]
        identifier = column.startswith(("CD_", "ID_", "NU_"))
        if identifier:
            score += 30; reasons.append("prefixo identificador")
        entity = column.split("_", 1)[1] if "_" in column else column
        semantic_hits = sum(entity in table for table in (left, right))
        if semantic_hits:
            score += 20 + 10 * (semantic_hits == 2); reasons.append("nome da entidade aparece na tabela")
        if frequency > 2:
            penalty = min(25, (frequency - 2) * 5); score -= penalty; reasons.append(f"coluna ocorre em {frequency} tabelas")
        if column in GENERIC or not identifier:
            score -= 25; reasons.append("campo genérico/não identificador")
        return max(0, min(100, score)), reasons

    def direct(self, source: str, target: str) -> RelationshipCandidate:
        source, target = source.upper(), target.upper()
        matches = [r for r in self.candidates if {r.source_table, r.target_table} == {source, target}]
        if not matches:
            raise RelationshipNotFoundError(f"Nenhum relacionamento candidato entre {source} e {target}")
        return max(matches, key=lambda r: r.score)

    def find_paths(self, source: str, target: str, limit: int = 3, minimum: Confidence = Confidence.MEDIUM) -> list[RelationshipPath]:
        source, target = self.catalog.get_table(source).name, self.catalog.get_table(target).name
        allowed = {Confidence.HIGH, Confidence.MEDIUM} if minimum != Confidence.LOW else set(Confidence)
        graph: dict[str, list[tuple[str, RelationshipCandidate]]] = defaultdict(list)
        for rel in self.candidates:
            if rel.confidence in allowed:
                graph[rel.source_table].append((rel.target_table, rel)); graph[rel.target_table].append((rel.source_table, rel))
        found: list[RelationshipPath] = []
        queue = deque([(source, [source], [])])
        while queue and len(found) < limit:
            node, tables, edges = queue.popleft()
            if node == target:
                score = min((e.score for e in edges), default=100)
                found.append(RelationshipPath(tables=tables, relationships=edges,
                    confidence=Confidence.HIGH if score >= 75 else Confidence.MEDIUM if score >= 50 else Confidence.LOW, score=score))
                continue
            for neighbor, edge in sorted(graph[node], key=lambda x: -x[1].score):
                if neighbor not in tables:
                    queue.append((neighbor, tables + [neighbor], edges + [edge]))
        if not found:
            raise PathNotFoundError("Não foi possível determinar um relacionamento confiável com os metadados disponíveis.")
        return sorted(found, key=lambda p: (len(p.relationships), -p.score))
