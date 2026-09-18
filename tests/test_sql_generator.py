from datetime import date

import pytest

from data_engineering_mcp.exceptions import AmbiguousColumnError, ColumnNotFoundError, InvalidFilterError, RelationshipNotFoundError, TableNotFoundError
from data_engineering_mcp.catalog import Catalog
from data_engineering_mcp.models import Cardinality, FilterCondition, KeyConstraint, KeyKind, RelationshipAuthority, RelationshipDecision, SqlGenerationRequest
from data_engineering_mcp.relationships import RelationshipEngine
from data_engineering_mcp.sql_generator import SQLGenerator
from conftest import make_xlsx


def approve_relationships(relationships):
    decision = RelationshipDecision(id="REL-TEST", date=date(2026, 9, 11), decided_by="HUMAN/Product Owner")
    relationships.candidates = [
        relationship.model_copy(update={"authority": RelationshipAuthority.APPROVED, "decision": decision})
        for relationship in relationships.candidates
    ]


def authorize_preserving_edge(relationships, source, target, *, cardinality=Cardinality.MANY_TO_ONE):
    decision = RelationshipDecision(id="REL-GRAIN", date=date(2026, 9, 18), decided_by="HUMAN/Product Owner")
    relationship = relationships.direct(source, target)
    if relationship.source_table != source:
        cardinality = {
            Cardinality.MANY_TO_ONE: Cardinality.ONE_TO_MANY,
            Cardinality.ONE_TO_MANY: Cardinality.MANY_TO_ONE,
        }.get(cardinality, cardinality)
    approved = relationship.model_copy(update={
        "authority": RelationshipAuthority.APPROVED,
        "decision": decision,
        "cardinality": cardinality,
        "cardinality_source": "ddl:test",
        "cardinality_authority": RelationshipAuthority.KNOWN,
    })
    relationships.candidates = [approved if candidate is relationship else candidate for candidate in relationships.candidates]
    target_column = approved.target_column if approved.target_table == target else approved.source_column
    relationships.keys.append(KeyConstraint(
        table=target, columns=[target_column], kind=KeyKind.PRIMARY_KEY,
        source="ddl:test", authority=RelationshipAuthority.KNOWN,
    ))


def test_single_table_select(stack):
    *_, generator = stack
    result = generator.generate_select("RAW_HAP_TB_PESSOA", ["CD_PESSOA"])
    assert result.sql.startswith("SELECT") and "FROM RAW_HAP_TB_PESSOA" in result.sql


def test_two_and_three_table_joins_with_aliases(stack):
    _, relationships, generator = stack
    approve_relationships(relationships)
    two = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"], columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"]))
    assert "LEFT JOIN RAW_HAP_TB_PESSOA" in two.sql and ".CD_PESSOA" in two.sql
    three = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PLANO"], columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL", "NM_PLANO"]))
    assert three.sql.count("LEFT JOIN") == 2


@pytest.mark.parametrize("authority", [None, RelationshipAuthority.INFERRED, RelationshipAuthority.KNOWN])
def test_join_requires_approved_authority_even_with_acceptable_confidence(stack, authority):
    _, relationships, generator = stack
    relationship = relationships.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    relationships.candidates = [relationship.model_copy(update={"authority": authority})]

    with pytest.raises(RelationshipNotFoundError) as error:
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
            columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
            allow_low_confidence=True,
        ))

    message = str(error.value)
    assert "RAW_HAP_TB_PESSOA.CD_PESSOA" in message
    assert "RAW_HAP_TB_USUARIO.CD_PESSOA" in message
    expected_authority = authority.value if authority is not None else "AUSENTE"
    assert f"autoridade {expected_authority}" in message
    assert "homologação como APPROVED" in message


def test_approved_relationship_with_conflict_is_blocked(stack):
    _, relationships, generator = stack
    approve_relationships(relationships)
    relationship = relationships.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    relationships.candidates = [relationship.model_copy(update={"conflicts": ["endpoints divergentes"]})]

    with pytest.raises(RelationshipNotFoundError, match=r"conflito\(s\): endpoints divergentes.*livre de conflitos"):
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
            columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
            allow_low_confidence=True,
        ))


def test_blocked_best_candidate_does_not_select_alternative(stack):
    _, relationships, generator = stack
    primary = relationships.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    decision = RelationshipDecision(id="REL-ALT", date=date(2026, 9, 11), decided_by="HUMAN/Product Owner")
    alternative = primary.model_copy(update={
        "source_column": "CD_USUARIO",
        "target_column": "CD_PESSOA",
        "score": primary.score - 1,
        "authority": RelationshipAuthority.APPROVED,
        "decision": decision,
    })
    relationships.candidates = [primary, alternative]

    with pytest.raises(RelationshipNotFoundError, match="autoridade INFERRED"):
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
            columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
        ))


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


def test_single_table_does_not_require_relationship_authority(stack):
    _, relationships, generator = stack
    relationships.candidates = []
    result = generator.generate_select("RAW_HAP_TB_USUARIO", ["CD_USUARIO"])
    assert "LEFT JOIN" not in result.sql


@pytest.mark.parametrize("cardinality", [Cardinality.MANY_TO_ONE, Cardinality.ONE_TO_ONE])
def test_grain_requires_authorized_cardinality_and_matching_unique_key(stack, cardinality):
    _, relationships, generator = stack
    authorize_preserving_edge(relationships, "RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA", cardinality=cardinality)
    result = generator.generate(SqlGenerationRequest(
        tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
        columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
        grain=["RAW_HAP_TB_USUARIO.CD_USUARIO"],
    ))
    assert "LEFT JOIN RAW_HAP_TB_PESSOA" in result.sql


@pytest.mark.parametrize("cardinality", [Cardinality.ONE_TO_MANY, Cardinality.MANY_TO_MANY, Cardinality.UNKNOWN])
def test_grain_blocks_multiplying_or_unknown_cardinality_without_sql(stack, cardinality):
    _, relationships, generator = stack
    approve_relationships(relationships)
    relationship = relationships.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    update = {"cardinality": cardinality}
    if cardinality != Cardinality.UNKNOWN:
        update |= {"cardinality_source": "ddl:test", "cardinality_authority": RelationshipAuthority.KNOWN}
    relationships.candidates = [relationship.model_copy(update=update)]
    with pytest.raises(RelationshipNotFoundError) as error:
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"],
            columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL"],
            grain=["RAW_HAP_TB_USUARIO.CD_USUARIO"],
        ))
    assert "Preservação de grão bloqueada" in str(error.value)
    assert "deduplicação automática" in str(error.value)
    assert "SELECT" not in str(error.value)


def test_grain_blocks_when_unique_key_is_missing_and_legacy_without_grain_still_works(stack):
    _, relationships, generator = stack
    approve_relationships(relationships)
    relationship = relationships.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    relationships.candidates = [relationship.model_copy(update={
        "cardinality": Cardinality.MANY_TO_ONE,
        "cardinality_source": "ddl:test",
        "cardinality_authority": RelationshipAuthority.KNOWN,
    })]
    with pytest.raises(RelationshipNotFoundError, match="unicidade não comprovada"):
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"], grain=["CD_USUARIO"],
        ))
    legacy = generator.generate(SqlGenerationRequest(tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"]))
    assert "LEFT JOIN" in legacy.sql


def test_three_table_authorized_fixture_preserves_one_row_per_user(stack):
    _, relationships, generator = stack
    authorize_preserving_edge(relationships, "RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    authorize_preserving_edge(relationships, "RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PLANO")
    result = generator.generate(SqlGenerationRequest(
        tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PLANO"],
        columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL", "NM_PLANO"],
        grain=["CD_USUARIO"],
    ))
    assert result.sql.count("LEFT JOIN") == 2


def test_real_three_table_grain_remains_blocked_without_new_hap_facts(stack):
    *_, generator = stack
    with pytest.raises(RelationshipNotFoundError) as error:
        generator.generate(SqlGenerationRequest(
            tables=["RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PLANO"],
            columns=["CD_USUARIO", "NM_PESSOA_RAZAO_SOCIAL", "NM_PLANO"],
            grain=["CD_USUARIO"],
        ))
    message = str(error.value)
    assert "autoridade INFERRED" in message
    assert "SELECT" not in message
    assert "ROW_NUMBER" not in message


def test_composite_join_emits_all_ordered_predicates(tmp_path):
    make_xlsx(tmp_path / "TABELA_A.xlsx", ["ID_B", "VERSAO_B", "VALOR"])
    make_xlsx(tmp_path / "TABELA_B.xlsx", ["ID_B", "VERSAO_B", "DESCRICAO"])
    catalog = Catalog(tmp_path); catalog.load(strict=True)
    relationships = RelationshipEngine(catalog); relationships.infer()
    relationship = relationships.direct("TABELA_A", "TABELA_B")
    decision = RelationshipDecision(id="REL-COMPOSITE", date=date(2026, 9, 18), decided_by="HUMAN/Product Owner")
    relationships.candidates = [relationship.model_copy(update={
        "authority": RelationshipAuthority.APPROVED,
        "decision": decision,
        "source_columns": ["ID_B", "VERSAO_B"],
        "target_columns": ["ID_B", "VERSAO_B"],
        "source_column": None,
        "target_column": None,
    })]
    generator = SQLGenerator(catalog, relationships)
    result = generator.generate(SqlGenerationRequest(tables=["TABELA_A", "TABELA_B"], columns=["TABELA_A.VALOR", "TABELA_B.DESCRICAO"]))
    assert "tb.ID_B = ta.ID_B" in result.sql
    assert "    AND tb.VERSAO_B = ta.VERSAO_B" in result.sql
