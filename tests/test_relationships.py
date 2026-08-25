import pytest

from data_engineering_mcp.catalog import Catalog
from data_engineering_mcp.exceptions import PathNotFoundError
from data_engineering_mcp.models import Confidence
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
