import pytest

from data_engineering_mcp.exceptions import AmbiguousColumnError, ColumnNotFoundError, InvalidFilterError, RelationshipNotFoundError, TableNotFoundError
from data_engineering_mcp.models import FilterCondition, SqlGenerationRequest


def test_single_table_select(stack):
    *_, generator = stack
    result = generator.generate_select("RAW_HAP_TB_PESSOA", ["CD_PESSOA"])
    assert result.sql.startswith("SELECT") and "FROM RAW_HAP_TB_PESSOA" in result.sql


def test_two_and_three_table_joins_with_aliases(stack):
    *_, generator = stack
    two = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"], columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"]))
    assert "LEFT JOIN RAW_HAP_TB_PESSOA" in two.sql and ".CD_PESSOA" in two.sql
    three = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PLANO"], columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL", "NM_PLANO"]))
    assert three.sql.count("LEFT JOIN") == 2


def test_parameterized_filter(stack):
    *_, generator = stack
    result = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO"], columns=["CD_USUARIO"], filters=[FilterCondition(column="FL_STATUS_USUARIO", operator="=", value=2)]))
    assert "= :p1" in result.sql and result.parameters == {"p1": 2} and "2" not in result.sql


def test_missing_table_column_ambiguity_and_relationship(stack):
    *_, generator = stack
    with pytest.raises(TableNotFoundError): generator.generate_select("NOPE")
    with pytest.raises(ColumnNotFoundError): generator.generate_select("RAW_HAP_TB_USUARIO", ["NOPE"])
    with pytest.raises(AmbiguousColumnError): generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PLANO"], columns=["CD_PLANO"]))
    with pytest.raises(RelationshipNotFoundError): generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PRECO_PLANO"], columns=["NM_PESSOA_RAZAO_SOCIAL", "VL_MENSALIDADE"]))


def test_invalid_filter(stack):
    *_, generator = stack
    with pytest.raises(InvalidFilterError): generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO"], filters=[FilterCondition(column="NOPE", operator="=", value=1)]))
