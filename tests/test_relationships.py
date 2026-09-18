import json
from datetime import date

import pytest

from data_engineering_mcp.catalog import Catalog
from data_engineering_mcp.exceptions import PathNotFoundError
from data_engineering_mcp.models import Cardinality, Confidence, ExplicitRelationship, RelationshipAuthority, RelationshipDecision
from data_engineering_mcp.relationships import RelationshipEngine
from conftest import make_xlsx


def test_expected_generic_candidates(stack):
    _, engine, _ = stack
    assert engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA").source_column == "CD_PESSOA"
    assert engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PLANO").source_column == "CD_PLANO"
    assert any(
        r.source_column == "CD_TABELA"
        and {r.source_table, r.target_table} == {"RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PRECO_PLANO"}
        for r in engine.candidates
    )


def test_generic_column_is_low(tmp_path):
    make_xlsx(tmp_path / "ALFA.xlsx", ["DT_PROCESSAMENTO"]); make_xlsx(tmp_path / "BETA.xlsx", ["DT_PROCESSAMENTO"])
    catalog = Catalog(tmp_path); catalog.load(strict=True); engine = RelationshipEngine(catalog); engine.infer()
    assert engine.candidates[0].confidence == Confidence.LOW


def test_path_and_absence(stack, tmp_path):
    catalog, engine, _ = stack
    paths = engine.find_paths("RAW_HAP_TB_PESSOA", "RAW_HAP_TB_PLANO")
    assert paths and "RAW_HAP_TB_USUARIO" in paths[0].tables
    make_xlsx(data_dir := tmp_path / "isolated.xlsx", ["ID_OTHER"])
    catalog.load(strict=True); engine.infer()
    with pytest.raises(PathNotFoundError): engine.find_paths("ISOLATED", "RAW_HAP_TB_PESSOA")


def test_multiple_paths(stack):
    _, engine, _ = stack
    paths = engine.find_paths("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PLANO")
    assert 1 <= len(paths) <= 3


def write_metadata(path, relationships, keys=None):
    payload = {"relationships": relationships}
    if keys is not None:
        payload["keys"] = keys
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_inferred_relationship_exposes_authority_and_source(stack):
    _, engine, _ = stack
    relationship = engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    assert relationship.authority == RelationshipAuthority.INFERRED
    assert relationship.source == "heuristic:matching-column-name"
    assert relationship.decision is None
    assert relationship.conflicts == []


def test_explicit_known_precedes_matching_inference(data_dir, tmp_path):
    metadata = tmp_path / "relationships.json"
    write_metadata(metadata, [{
        "source_table": "raw_hap_tb_usuario", "source_column": "cd_pessoa",
        "target_table": "raw_hap_tb_pessoa", "target_column": "cd_pessoa",
        "authority": "KNOWN", "source": "data-contract:crm-v1",
    }])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    relationship = engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    assert relationship.authority == RelationshipAuthority.KNOWN
    assert relationship.source == "data-contract:crm-v1"
    assert "metadado explícito prevalece" in relationship.rationale


def test_approved_requires_complete_human_decision(data_dir, tmp_path):
    metadata = tmp_path / "relationships.json"
    base = {
        "source_table": "RAW_HAP_TB_USUARIO", "source_column": "CD_PESSOA",
        "target_table": "RAW_HAP_TB_PESSOA", "target_column": "CD_PESSOA",
        "authority": "APPROVED", "source": "decision:G2-SPEC-002",
    }
    write_metadata(metadata, [base])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    with pytest.raises(ValueError, match="APPROVED"):
        RelationshipEngine(catalog, metadata).infer()

    base["decision"] = {"id": "G2-SPEC-002", "date": "2026-09-11", "decided_by": "HUMAN/Product Owner"}
    write_metadata(metadata, [base])
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    relationship = engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    assert relationship.authority == RelationshipAuthority.APPROVED
    assert relationship.decision.id == "G2-SPEC-002"


def test_conflicting_endpoints_are_visible_and_deterministic(data_dir, tmp_path):
    metadata = tmp_path / "relationships.json"
    write_metadata(metadata, [{
        "source_table": "RAW_HAP_TB_USUARIO", "source_column": "CD_PESSOA",
        "target_table": "RAW_HAP_TB_PESSOA", "target_column": "NM_PESSOA_RAZAO_SOCIAL",
        "authority": "KNOWN", "source": "manual:catalog",
    }])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    first = RelationshipEngine(catalog, metadata); first.infer()
    second = RelationshipEngine(catalog, metadata); second.infer()
    assert [r.model_dump() for r in first.candidates] == [r.model_dump() for r in second.candidates]
    matches = [r for r in first.candidates if {r.source_table, r.target_table} == {"RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"}]
    assert matches and all(r.conflicts for r in matches)
    assert all(r.authority != RelationshipAuthority.APPROVED for r in matches)


def test_missing_file_preserves_inference_and_invalid_json_fails(data_dir, tmp_path):
    catalog = Catalog(data_dir); catalog.load(strict=True)
    missing = RelationshipEngine(catalog, tmp_path / "missing.json"); missing.infer()
    assert missing.candidates and all(r.authority == RelationshipAuthority.INFERRED for r in missing.candidates)
    invalid = tmp_path / "relationships.json"; invalid.write_text("{invalid", encoding="utf-8")
    with pytest.raises(ValueError, match="Metadado de relacionamentos inválido"):
        RelationshipEngine(catalog, invalid).infer()


def test_legacy_document_and_explicit_simple_composite_keys(data_dir, tmp_path):
    catalog = Catalog(data_dir); catalog.load(strict=True)
    legacy = tmp_path / "legacy.json"; write_metadata(legacy, [])
    legacy_engine = RelationshipEngine(catalog, legacy); legacy_engine.infer()
    assert legacy_engine.keys == []

    metadata = tmp_path / "relationships.json"
    write_metadata(metadata, [], [
        {"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "PRIMARY_KEY", "source": "ddl:crm-v1", "authority": "KNOWN"},
        {"table": "RAW_HAP_TB_USUARIO", "columns": ["CD_PESSOA", "CD_PLANO"], "kind": "UNIQUE", "source": "decision:KEY-TEST", "authority": "APPROVED", "decision": {"id": "KEY-TEST", "date": "2026-09-18", "decided_by": "HUMAN/Product Owner"}},
    ])
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    assert engine.keys_for_table("RAW_HAP_TB_PESSOA")[0].columns == ["CD_PESSOA"]
    assert engine.keys_for_table("RAW_HAP_TB_USUARIO")[0].columns == ["CD_PESSOA", "CD_PLANO"]
    assert engine.keys_for_table("RAW_HAP_TB_PESSOA")[0].authority == RelationshipAuthority.KNOWN
    assert engine.keys_for_table("RAW_HAP_TB_USUARIO")[0].authority == RelationshipAuthority.APPROVED


@pytest.mark.parametrize("key_update,match", [
    ({"columns": []}, "at least 1"),
    ({"columns": ["NOPE"]}, "inexistente"),
    ({"columns": ["CD_PESSOA", "CD_PESSOA"]}, "duplicadas"),
    ({"authority": "APPROVED"}, "APPROVED"),
    ({"extra": "no"}, "extra"),
])
def test_invalid_key_metadata_fails_closed(data_dir, tmp_path, key_update, match):
    key = {"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "UNIQUE", "source": "ddl:test", "authority": "KNOWN"}
    key.update(key_update)
    metadata = tmp_path / "relationships.json"; write_metadata(metadata, [], [key])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    with pytest.raises(ValueError, match=match):
        RelationshipEngine(catalog, metadata).infer()


def test_cardinality_is_independent_oriented_and_conflicts_are_visible(data_dir, tmp_path):
    relation = {
        "source_table": "RAW_HAP_TB_USUARIO", "source_column": "CD_PESSOA",
        "target_table": "RAW_HAP_TB_PESSOA", "target_column": "CD_PESSOA",
        "authority": "KNOWN", "source": "contract:rel-v1",
        "cardinality": "MANY_TO_ONE", "cardinality_source": "ddl:fk-v1", "cardinality_authority": "KNOWN",
    }
    metadata = tmp_path / "relationships.json"
    write_metadata(metadata, [relation], [{"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "PRIMARY_KEY", "source": "ddl:pk-v1", "authority": "KNOWN"}])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    candidate = engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    assert candidate.authority == RelationshipAuthority.KNOWN
    assert candidate.cardinality_authority == RelationshipAuthority.KNOWN
    assert engine.oriented_cardinality(candidate, "RAW_HAP_TB_USUARIO") == Cardinality.MANY_TO_ONE
    assert engine.oriented_cardinality(candidate, "RAW_HAP_TB_PESSOA") == Cardinality.ONE_TO_MANY
    assert engine.grain_preservation(candidate, "RAW_HAP_TB_USUARIO")["preserves_grain"] is True
    assert engine.grain_preservation(candidate, "RAW_HAP_TB_PESSOA")["preserves_grain"] is False

    conflicting = relation | {"cardinality": "ONE_TO_ONE", "cardinality_source": "dictionary:other"}
    write_metadata(metadata, [relation, conflicting], [{"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "PRIMARY_KEY", "source": "ddl:pk-v1", "authority": "KNOWN"}])
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    candidate = engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA")
    assert candidate.cardinality_conflicts
    assert engine.grain_preservation(candidate, "RAW_HAP_TB_USUARIO")["preserves_grain"] is False


def test_conflicting_keys_are_visible_and_block_preservation(data_dir, tmp_path):
    relation = {
        "source_table": "RAW_HAP_TB_USUARIO", "source_column": "CD_PESSOA",
        "target_table": "RAW_HAP_TB_PESSOA", "target_column": "CD_PESSOA",
        "authority": "KNOWN", "source": "contract:rel-v1",
        "cardinality": "MANY_TO_ONE", "cardinality_source": "ddl:fk-v1", "cardinality_authority": "KNOWN",
    }
    keys = [
        {"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "PRIMARY_KEY", "source": "ddl:one", "authority": "KNOWN"},
        {"table": "RAW_HAP_TB_PESSOA", "columns": ["CD_PESSOA"], "kind": "UNIQUE", "source": "dictionary:two", "authority": "KNOWN"},
    ]
    metadata = tmp_path / "relationships.json"; write_metadata(metadata, [relation], keys)
    catalog = Catalog(data_dir); catalog.load(strict=True)
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    key = engine.keys_for_table("RAW_HAP_TB_PESSOA")[0]
    assert key.conflicts
    proof = engine.grain_preservation(engine.direct("RAW_HAP_TB_USUARIO", "RAW_HAP_TB_PESSOA"), "RAW_HAP_TB_USUARIO")
    assert proof["preserves_grain"] is False and "conflito(s) de chave" in proof["reasons"][0]


@pytest.mark.parametrize("update,match", [
    ({"cardinality": "INVALID"}, "cardinality"),
    ({"cardinality": "MANY_TO_ONE"}, "cardinality_source"),
    ({"cardinality": "MANY_TO_ONE", "cardinality_source": "ddl:test", "cardinality_authority": "APPROVED"}, "decisão"),
])
def test_invalid_cardinality_metadata_fails_closed(data_dir, tmp_path, update, match):
    relation = {
        "source_table": "RAW_HAP_TB_USUARIO", "source_column": "CD_PESSOA",
        "target_table": "RAW_HAP_TB_PESSOA", "target_column": "CD_PESSOA",
        "authority": "KNOWN", "source": "contract:rel-v1",
    }
    relation.update(update)
    metadata = tmp_path / "relationships.json"; write_metadata(metadata, [relation])
    catalog = Catalog(data_dir); catalog.load(strict=True)
    with pytest.raises(ValueError, match=match):
        RelationshipEngine(catalog, metadata).infer()


def _composite_metadata():
    return [{
        "source_table": "TABELA_A",
        "source_columns": ["ID_B", "VERSAO_B"],
        "target_table": "TABELA_B",
        "target_columns": ["ID_B", "VERSAO_B"],
        "authority": "APPROVED",
        "source": "decision:REL-COMPOSITE",
        "decision": {"id": "REL-COMPOSITE", "date": "2026-09-18", "decided_by": "HUMAN/Product Owner"},
        "cardinality": "MANY_TO_ONE",
        "cardinality_source": "ddl:test",
        "cardinality_authority": "KNOWN",
    }]


def _composite_stack(tmp_path, key_columns):
    make_xlsx(tmp_path / "TABELA_A.xlsx", ["ID_B", "VERSAO_B", "VALOR"])
    make_xlsx(tmp_path / "TABELA_B.xlsx", ["ID_B", "VERSAO_B", "DESCRICAO"])
    metadata = tmp_path / "relationships.json"
    write_metadata(metadata, _composite_metadata(), [{
        "table": "TABELA_B", "columns": key_columns, "kind": "UNIQUE",
        "source": "ddl:test", "authority": "KNOWN",
    }])
    catalog = Catalog(tmp_path); catalog.load(strict=True)
    engine = RelationshipEngine(catalog, metadata); engine.infer()
    return catalog, engine


def test_composite_relationship_preserves_grain_without_partial_heuristic_conflict(tmp_path):
    _, engine = _composite_stack(tmp_path, ["ID_B", "VERSAO_B"])
    relationship = engine.direct("TABELA_A", "TABELA_B")
    assert relationship.source_columns == ["ID_B", "VERSAO_B"]
    assert relationship.target_columns == ["ID_B", "VERSAO_B"]
    assert relationship.conflicts == []
    assert engine.grain_preservation(relationship, "TABELA_A")["status"] == "PRESERVES"


@pytest.mark.parametrize("key_columns", [["ID_B"], ["VERSAO_B", "ID_B"]])
def test_composite_relationship_blocks_partial_or_reordered_key(tmp_path, key_columns):
    _, engine = _composite_stack(tmp_path, key_columns)
    relationship = engine.direct("TABELA_A", "TABELA_B")
    proof = engine.grain_preservation(relationship, "TABELA_A")
    assert proof["status"] == "BLOCKED"
    assert proof["target_key"] is None


@pytest.mark.parametrize("payload,match", [
    ({"source_column": "ID_B", "target_columns": ["ID_B"]}, "mistura"),
    ({"source_columns": [], "target_columns": ["ID_B"]}, "ao menos uma"),
    ({"source_columns": ["ID_B"], "target_columns": ["ID_B", "VERSAO_B"]}, "mesmo tamanho"),
    ({"source_columns": ["ID_B", "ID_B"], "target_columns": ["ID_B", "VERSAO_B"]}, "duplicadas"),
])
def test_composite_relationship_input_fails_closed(payload, match):
    base = {
        "source_table": "TABELA_A", "target_table": "TABELA_B",
        "authority": "KNOWN", "source": "contract:test",
    } | payload
    with pytest.raises(ValueError, match=match):
        ExplicitRelationship.model_validate(base)


def test_legacy_and_unit_vector_relationships_have_same_identity():
    common = {
        "source_table": "TABELA_A", "target_table": "TABELA_B",
        "authority": "KNOWN", "source": "contract:test",
    }
    legacy = ExplicitRelationship.model_validate(common | {"source_column": "ID_B", "target_column": "ID_B"})
    vector = ExplicitRelationship.model_validate(common | {"source_columns": ["ID_B"], "target_columns": ["ID_B"]})
    assert legacy.source_columns == vector.source_columns == ["ID_B"]
    assert legacy.target_columns == vector.target_columns == ["ID_B"]
    assert ExplicitRelationship.model_validate(vector.model_dump()).source_columns == ["ID_B"]
