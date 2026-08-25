import pytest
from pydantic import ValidationError

from data_engineering_mcp.exceptions import ColumnNotFoundError, ForbiddenSQLOperationError
from data_engineering_mcp.models import FilterCondition, SqlGenerationRequest
from data_engineering_mcp.sql_explainer import explain_sql


@pytest.mark.parametrize("word", ["INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"])
def test_generated_sql_has_no_destructive_operations(stack, word):
    *_, generator = stack
    sql = generator.generate_select("RAW_HAP_TB_PESSOA").sql.upper()
    assert sql.startswith("SELECT") and word not in sql


def test_injection_cannot_enter_sql(stack):
    *_, generator = stack
    malicious = "2; DROP TABLE X"
    result = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO"], columns=["CD_USUARIO"], filters=[FilterCondition(column="FL_STATUS_USUARIO", operator="=", value=malicious)]))
    assert malicious not in result.sql and result.parameters["p1"] == malicious
    with pytest.raises(ColumnNotFoundError): generator.generate_select("RAW_HAP_TB_USUARIO", ["CD_USUARIO; DROP TABLE X"])


def test_operator_allowlist_and_explainer_guard():
    with pytest.raises(ValidationError): FilterCondition(column="X", operator="= 1; DROP", value=1)
    with pytest.raises(ForbiddenSQLOperationError): explain_sql("DELETE FROM X")
    assert explain_sql("SELECT X FROM T")["tabelas"] == ["T"]
