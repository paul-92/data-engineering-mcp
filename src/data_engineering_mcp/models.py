from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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


class RelationshipCandidate(BaseModel):
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    confidence: Confidence
    score: int = Field(ge=0, le=100)
    rationale: str


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


class SqlGenerationResult(BaseModel):
    sql: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    relationships: list[RelationshipCandidate] = Field(default_factory=list)
