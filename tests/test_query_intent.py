import pytest
from pydantic import ValidationError

from data_engineering_mcp.models import RelationshipAuthority
from data_engineering_mcp.query_intent import (
    FilterReference,
    OutputColumn,
    QueryFilter,
    QueryIntent,
    RelationshipIntent,
)


def test_minimal_intent_serializes_deterministically():
    intent = QueryIntent(
        sources=["CUSTOMERS"],
        output_columns=[OutputColumn(field="CUSTOMERS.ID")],
    )

    assert intent.to_json() == intent.to_json()
    assert intent.to_dict() == {
        "sources": ["CUSTOMERS"],
        "output_columns": [{"field": "CUSTOMERS.ID"}],
        "filters": [],
        "relationships": [],
        "warnings": [],
        "authority_pending": [],
    }
    assert "grain" not in intent.to_dict()


def test_complete_intent_covers_exactly_the_seven_elements():
    intent = QueryIntent(
        sources=["ORDERS", "CUSTOMERS"],
        output_columns=[OutputColumn(field="CUSTOMERS.NAME", alias="customer_name")],
        filters=[
            QueryFilter(field="ORDERS.STATUS", operator="=", value="OPEN"),
            QueryFilter(
                field="ORDERS.CUSTOMER_ID",
                operator="=",
                reference=FilterReference(field="CUSTOMERS.ID"),
            ),
        ],
        relationships=[
            RelationshipIntent(identity="REL-ORDERS-CUSTOMERS", authority="APPROVED")
        ],
        grain=["ORDERS.ID"],
        warnings=["Example warning"],
        authority_pending=["Confirm reporting scope"],
    )

    payload = intent.to_dict()
    assert list(payload) == [
        "sources",
        "output_columns",
        "filters",
        "relationships",
        "grain",
        "warnings",
        "authority_pending",
    ]
    assert payload["output_columns"][0]["alias"] == "customer_name"
    assert payload["filters"][1]["reference"] == {"field": "CUSTOMERS.ID"}
    assert payload["grain"] == ["ORDERS.ID"]


@pytest.mark.parametrize("authority", list(RelationshipAuthority))
def test_relationship_authority_is_preserved_without_promotion(authority):
    review = ["Relationship requires review"] if authority == RelationshipAuthority.INFERRED else []
    intent = QueryIntent(
        sources=["A", "B"],
        output_columns=[OutputColumn(field="A.ID")],
        relationships=[RelationshipIntent(identity="REL-1", authority=authority)],
        authority_pending=review,
    )

    assert intent.to_dict()["relationships"][0]["authority"] == authority.value


@pytest.mark.parametrize(
    "relationship",
    [
        RelationshipIntent(identity="REL-MISSING"),
        RelationshipIntent(identity="REL-INFERRED", authority="INFERRED"),
        RelationshipIntent(identity="REL-CONFLICT", authority="KNOWN", conflicts=["endpoint mismatch"]),
    ],
)
def test_authority_gap_or_conflict_must_remain_explicit(relationship):
    with pytest.raises(ValidationError, match="warnings or authority_pending"):
        QueryIntent(
            sources=["A", "B"],
            output_columns=[OutputColumn(field="A.ID")],
            relationships=[relationship],
        )

    explicit = QueryIntent(
        sources=["A", "B"],
        output_columns=[OutputColumn(field="A.ID")],
        relationships=[relationship],
        warnings=["Relationship authority requires review"],
    )
    assert explicit.warnings


def test_filter_rejects_value_and_reference_together():
    with pytest.raises(ValidationError, match="value or reference"):
        QueryFilter(field="A.ID", operator="=", value=1, reference={"field": "B.ID"})


def test_filter_requires_value_or_reference_but_accepts_explicit_null():
    with pytest.raises(ValidationError, match="requires value or reference"):
        QueryFilter(field="A.ID", operator="IS NULL")

    assert QueryFilter(field="A.ID", operator="IS NULL", value=None).value is None


def test_contract_has_no_sql_generation_behavior():
    assert not hasattr(QueryIntent, "generate")
    assert not hasattr(QueryIntent, "execute")
    assert "SQLGenerator" not in __import__(
        "data_engineering_mcp.query_intent", fromlist=["*"]
    ).__dict__
