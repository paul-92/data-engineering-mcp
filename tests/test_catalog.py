import time

import pytest

from data_engineering_mcp.catalog import Catalog, normalize_table_name
from data_engineering_mcp.exceptions import MissingHeaderError, NoValidWorksheetError
from conftest import make_xlsx


def test_normalization():
    assert normalize_table_name("rawzn.raw_hap_tb_usuario_SINTETICO.xlsx") == "RAW_HAP_TB_USUARIO"


def test_discovery_description_and_search(data_dir):
    catalog = Catalog(data_dir); catalog.load(strict=True)
    assert catalog.list_tables() == sorted(catalog.list_tables())
    table = catalog.get_table("raw_hap_tb_usuario")
    assert table.source_file.endswith("SINTETICO.xlsx") and table.worksheet == "Dados"
    assert [c.name for c in table.columns][:2] == ["CD_USUARIO", "NU_USUARIO"]
    assert "RAW_HAP_TB_USUARIO.CD_PLANO" in catalog.find_column("cd_plano")
    assert catalog.search_tables("plano") == ["RAW_HAP_TB_PLANO", "RAW_HAP_TB_PRECO_PLANO"]


def test_ignores_sql_sheet(tmp_path):
    make_xlsx(tmp_path / "T.xlsx", ["ID_OK"], sql_first=True)
    catalog = Catalog(tmp_path); catalog.load(strict=True)
    assert catalog.get_table("T").worksheet == "Dados"


def test_invalid_and_missing_headers(tmp_path):
    (tmp_path / "bad.xlsx").write_bytes(b"not xlsx")
    with pytest.raises(NoValidWorksheetError): Catalog(tmp_path).load(strict=True)
    (tmp_path / "bad.xlsx").unlink(); make_xlsx(tmp_path / "empty.xlsx", [])
    with pytest.raises(MissingHeaderError): Catalog(tmp_path).load(strict=True)


def test_dynamic_add_remove_schema_and_timestamp(tmp_path):
    make_xlsx(tmp_path / "A.xlsx", ["CD_A"]); make_xlsx(tmp_path / "B.xlsx", ["CD_B"])
    catalog = Catalog(tmp_path); catalog.load(strict=True); before = catalog.loaded_at
    make_xlsx(tmp_path / "C.xlsx", ["CD_C"]); change = catalog.load(strict=True)
    assert change.added == ["C"] and catalog.loaded_at >= before
    (tmp_path / "B.xlsx").unlink(); make_xlsx(tmp_path / "A.xlsx", ["CD_A", "NM_A"])
    change = catalog.load(strict=True)
    assert change.removed == ["B"] and change.schemas_changed == ["A"]
