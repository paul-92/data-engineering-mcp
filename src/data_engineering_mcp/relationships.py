from __future__ import annotations

from collections import Counter, defaultdict, deque

from .catalog import Catalog
from .exceptions import PathNotFoundError, RelationshipNotFoundError
from .models import Confidence, RelationshipCandidate, RelationshipPath

GENERIC = {"ID", "CODIGO", "CD", "STATUS", "FL_STATUS", "DT_PROCESSAMENTO", "DT_ATUALIZACAO", "NU_SEQ"}


class RelationshipEngine:
    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self.candidates: list[RelationshipCandidate] = []

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
        self.candidates = sorted(result, key=lambda r: (-r.score, r.source_table, r.target_table, r.source_column))
        return self.candidates

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
