from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import RelationshipAuthority


class IntentModel(BaseModel):
    """Base estrita para o contrato declarativo de intenção."""

    model_config = ConfigDict(extra="forbid")


class OutputColumn(IntentModel):
    field: str = Field(min_length=1)
    alias: str | None = Field(default=None, min_length=1)


class FilterReference(IntentModel):
    field: str = Field(min_length=1)


class QueryFilter(IntentModel):
    field: str = Field(min_length=1)
    operator: str = Field(min_length=1)
    value: Any = None
    reference: FilterReference | None = None

    @model_validator(mode="after")
    def value_or_reference(self) -> "QueryFilter":
        if self.reference is not None and "value" in self.model_fields_set:
            raise ValueError("filter accepts value or reference, not both")
        if self.reference is None and "value" not in self.model_fields_set:
            raise ValueError("filter requires value or reference")
        return self


class RelationshipIntent(IntentModel):
    identity: str = Field(min_length=1)
    authority: RelationshipAuthority | None = None
    conflicts: list[str] = Field(default_factory=list)


class QueryIntent(IntentModel):
    """Revisable query intent; it does not plan, generate, or execute SQL."""

    sources: list[str] = Field(min_length=1)
    output_columns: list[OutputColumn] = Field(min_length=1)
    filters: list[QueryFilter] = Field(default_factory=list)
    relationships: list[RelationshipIntent] = Field(default_factory=list)
    grain: list[str] | None = None
    warnings: list[str] = Field(default_factory=list)
    authority_pending: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def keep_authority_gaps_explicit(self) -> "QueryIntent":
        needs_review = any(
            relationship.authority in (None, RelationshipAuthority.INFERRED)
            or relationship.conflicts
            for relationship in self.relationships
        )
        if needs_review and not (self.warnings or self.authority_pending):
            raise ValueError(
                "INFERRED, conflicting, or absent relationship authority must remain "
                "explicit in warnings or authority_pending"
            )
        return self

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)
