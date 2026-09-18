from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ColumnSchema(BaseModel):
    name: str
    position: int


class TableSchema(BaseModel):
    name: str
    source_file: str
    worksheet: str
    columns: list[ColumnSchema]

    @property
    def column_count(self) -> int:
        return len(self.columns)


class Confidence(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RelationshipAuthority(StrEnum):
    INFERRED = "INFERRED"
    KNOWN = "KNOWN"
    APPROVED = "APPROVED"


class Cardinality(StrEnum):
    ONE_TO_ONE = "ONE_TO_ONE"
    MANY_TO_ONE = "MANY_TO_ONE"
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_MANY = "MANY_TO_MANY"
    UNKNOWN = "UNKNOWN"


class KeyKind(StrEnum):
    PRIMARY_KEY = "PRIMARY_KEY"
    UNIQUE = "UNIQUE"


class RelationshipDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    date: date
    decided_by: Literal["HUMAN/Product Owner"]


class RelationshipCandidate(BaseModel):
    source_table: str
    source_column: str | None = None
    source_columns: list[str] | None = None
    target_table: str
    target_column: str | None = None
    target_columns: list[str] | None = None
    confidence: Confidence
    score: int = Field(ge=0, le=100)
    rationale: str
    authority: RelationshipAuthority = RelationshipAuthority.INFERRED
    source: str = "heuristic:matching-column-name"
    decision: RelationshipDecision | None = None
    conflicts: list[str] = Field(default_factory=list)
    cardinality: Cardinality = Cardinality.UNKNOWN
    cardinality_source: str | None = None
    cardinality_authority: RelationshipAuthority | None = None
    cardinality_decision: RelationshipDecision | None = None
    cardinality_conflicts: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_endpoints(cls, data: Any) -> Any:
        return _normalize_relationship_endpoints(data, strict_input=False)

    @model_validator(mode="after")
    def validate_authority(self) -> "RelationshipCandidate":
        if self.authority == RelationshipAuthority.APPROVED and self.decision is None:
            raise ValueError("APPROVED exige decision.id, decision.date e decision.decided_by=HUMAN/Product Owner")
        if self.authority != RelationshipAuthority.APPROVED and self.decision is not None:
            raise ValueError("decision só é permitido para relacionamentos APPROVED")
        if self.cardinality_authority == RelationshipAuthority.INFERRED:
            raise ValueError("cardinality_authority não aceita INFERRED")
        if self.cardinality == Cardinality.UNKNOWN:
            if any((self.cardinality_source, self.cardinality_authority, self.cardinality_decision)):
                raise ValueError("cardinalidade UNKNOWN não pode declarar autoridade, fonte ou decisão")
        elif not self.cardinality_source or self.cardinality_authority is None:
            raise ValueError("cardinalidade explícita exige cardinality_source e cardinality_authority")
        if self.cardinality_authority == RelationshipAuthority.APPROVED and self.cardinality_decision is None:
            raise ValueError("cardinalidade APPROVED exige decisão HUMAN registrada")
        if self.cardinality_authority != RelationshipAuthority.APPROVED and self.cardinality_decision is not None:
            raise ValueError("cardinality_decision só é permitido para cardinalidade APPROVED")
        return self


class ExplicitRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_table: str = Field(min_length=1)
    source_column: str | None = None
    source_columns: list[str] | None = None
    target_table: str = Field(min_length=1)
    target_column: str | None = None
    target_columns: list[str] | None = None
    source: str = Field(min_length=1)
    authority: Literal[RelationshipAuthority.KNOWN, RelationshipAuthority.APPROVED]
    decision: RelationshipDecision | None = None
    cardinality: Cardinality = Cardinality.UNKNOWN
    cardinality_source: str | None = None
    cardinality_authority: Literal[RelationshipAuthority.KNOWN, RelationshipAuthority.APPROVED] | None = None
    cardinality_decision: RelationshipDecision | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_endpoints(cls, data: Any) -> Any:
        return _normalize_relationship_endpoints(data, strict_input=True)

    @field_validator("source_table", "target_table")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source não pode ser vazio")
        return value

    @field_validator("cardinality_source")
    @classmethod
    def normalize_cardinality_source(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("cardinality_source não pode ser vazio")
        return value

    @model_validator(mode="after")
    def validate_decision(self) -> "ExplicitRelationship":
        if self.authority == RelationshipAuthority.APPROVED and self.decision is None:
            raise ValueError("APPROVED exige decisão registrada do HUMAN/Product Owner")
        if self.authority == RelationshipAuthority.KNOWN and self.decision is not None:
            raise ValueError("KNOWN não pode conter decision; use APPROVED")
        if self.cardinality == Cardinality.UNKNOWN:
            if any((self.cardinality_source, self.cardinality_authority, self.cardinality_decision)):
                raise ValueError("cardinalidade UNKNOWN não pode declarar autoridade, fonte ou decisão")
        elif not self.cardinality_source or self.cardinality_authority is None:
            raise ValueError("cardinalidade explícita exige cardinality_source e cardinality_authority")
        if self.cardinality_authority == RelationshipAuthority.APPROVED and self.cardinality_decision is None:
            raise ValueError("cardinalidade APPROVED exige decisão registrada do HUMAN/Product Owner")
        if self.cardinality_authority == RelationshipAuthority.KNOWN and self.cardinality_decision is not None:
            raise ValueError("cardinalidade KNOWN não pode conter cardinality_decision")
        return self


def _normalize_relationship_endpoints(data: Any, *, strict_input: bool) -> Any:
    if not isinstance(data, dict):
        return data
    normalized = dict(data)
    scalar_present = any(normalized.get(name) is not None for name in ("source_column", "target_column"))
    vector_present = any(normalized.get(name) is not None for name in ("source_columns", "target_columns"))
    scalar_complete = all(normalized.get(name) is not None for name in ("source_column", "target_column"))
    vector_complete = all(normalized.get(name) is not None for name in ("source_columns", "target_columns"))

    equivalent_unit_vector = (
        scalar_present
        and vector_present
        and scalar_complete
        and vector_complete
        and len(normalized["source_columns"]) == 1
        and len(normalized["target_columns"]) == 1
        and normalized["source_column"] == normalized["source_columns"][0]
        and normalized["target_column"] == normalized["target_columns"][0]
    )
    if strict_input and scalar_present and vector_present and not equivalent_unit_vector:
        raise ValueError("relacionamento não aceita mistura de campos escalares e listas")
    if scalar_present and not scalar_complete:
        raise ValueError("source_column e target_column devem ser informados juntos")
    if vector_present and not vector_complete:
        raise ValueError("source_columns e target_columns devem ser informados juntos")
    if not scalar_complete and not vector_complete:
        raise ValueError("relacionamento exige endpoints escalares ou listas de colunas")

    if vector_complete:
        source_columns = _normalize_endpoint_columns(normalized["source_columns"], "source_columns")
        target_columns = _normalize_endpoint_columns(normalized["target_columns"], "target_columns")
        if len(source_columns) != len(target_columns):
            raise ValueError("source_columns e target_columns devem ter o mesmo tamanho")
        normalized["source_columns"] = source_columns
        normalized["target_columns"] = target_columns
        if len(source_columns) == 1:
            normalized.setdefault("source_column", source_columns[0])
            normalized.setdefault("target_column", target_columns[0])
        elif not strict_input:
            normalized["source_column"] = None
            normalized["target_column"] = None
    else:
        source_column = _normalize_endpoint_column(normalized["source_column"], "source_column")
        target_column = _normalize_endpoint_column(normalized["target_column"], "target_column")
        normalized["source_column"] = source_column
        normalized["target_column"] = target_column
        normalized["source_columns"] = [source_column]
        normalized["target_columns"] = [target_column]
    return normalized


def _normalize_endpoint_column(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} não aceita identificador vazio")
    return value.strip().upper()


def _normalize_endpoint_columns(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} deve conter ao menos uma coluna")
    columns = [_normalize_endpoint_column(column, field) for column in value]
    if len(columns) != len(set(columns)):
        raise ValueError(f"{field} não aceita colunas duplicadas")
    return columns


class ExplicitKey(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table: str = Field(min_length=1)
    columns: list[str] = Field(min_length=1)
    kind: KeyKind
    source: str = Field(min_length=1)
    authority: Literal[RelationshipAuthority.KNOWN, RelationshipAuthority.APPROVED]
    decision: RelationshipDecision | None = None

    @field_validator("table")
    @classmethod
    def normalize_table(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source não pode ser vazio")
        return value

    @field_validator("columns")
    @classmethod
    def normalize_columns(cls, value: list[str]) -> list[str]:
        normalized = [column.strip().upper() for column in value]
        if any(not column for column in normalized):
            raise ValueError("columns não aceita identificador vazio")
        if len(normalized) != len(set(normalized)):
            raise ValueError("columns não aceita colunas duplicadas")
        return normalized

    @model_validator(mode="after")
    def validate_decision(self) -> "ExplicitKey":
        if self.authority == RelationshipAuthority.APPROVED and self.decision is None:
            raise ValueError("chave APPROVED exige decisão registrada do HUMAN/Product Owner")
        if self.authority == RelationshipAuthority.KNOWN and self.decision is not None:
            raise ValueError("chave KNOWN não pode conter decision")
        return self


class KeyConstraint(ExplicitKey):
    conflicts: list[str] = Field(default_factory=list)


class RelationshipMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relationships: list[ExplicitRelationship]
    keys: list[ExplicitKey] = Field(default_factory=list)


class RelationshipPath(BaseModel):
    tables: list[str]
    relationships: list[RelationshipCandidate]
    confidence: Confidence
    score: int


class CatalogStatus(BaseModel):
    file_count: int
    table_count: int
    total_columns: int
    loaded_at: datetime
    tables: list[str]
    relationship_count: int


class CatalogChange(BaseModel):
    previous_table_count: int
    current_table_count: int
    added: list[str]
    removed: list[str]
    schemas_changed: list[str]
    new_relationships: int
    loaded_at: datetime
    errors: list[str] = Field(default_factory=list)


class FilterCondition(BaseModel):
    column: str
    operator: Literal["=", "<>", ">", ">=", "<", "<=", "IN", "IS NULL", "IS NOT NULL", "LIKE"]
    value: Any = None
    table: str | None = None

    @field_validator("operator", mode="before")
    @classmethod
    def normalize_operator(cls, value: str) -> str:
        return " ".join(value.upper().split())


class SqlGenerationRequest(BaseModel):
    tables: list[str] = Field(min_length=1)
    columns: list[str] | None = None
    filters: list[FilterCondition] | None = None
    allow_low_confidence: bool = False
    grain: list[str] | None = Field(default=None, min_length=1)


class SqlGenerationResult(BaseModel):
    sql: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    relationships: list[RelationshipCandidate] = Field(default_factory=list)
