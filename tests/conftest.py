from pathlib import Path

import pytest
from openpyxl import Workbook

from data_engineering_mcp.catalog import Catalog
from data_engineering_mcp.relationships import RelationshipEngine
from data_engineering_mcp.sql_generator import SQLGenerator


def make_xlsx(path: Path, headers: list[str], *, sql_first: bool = False) -> Path:
    wb = Workbook()
    ws = wb.active
    if sql_first:
        ws.title = "SQL"; ws.append(["SELECT * FROM X"]); ws = wb.create_sheet("Dados")
    else:
        ws.title = "Dados"
    ws.append(headers)
    wb.save(path)
    return path


@pytest.fixture
def data_dir(tmp_path):
    make_xlsx(tmp_path / "RAW_HAP_TB_USUARIO_SINTETICO.xlsx", ["CD_USUARIO", "NU_USUARIO", "CD_PESSOA", "CD_PLANO", "CD_TABELA", "FL_STATUS_USUARIO"])
    make_xlsx(tmp_path / "RAW_HAP_TB_PESSOA_SINTETICO.xlsx", ["CD_PESSOA", "NM_PESSOA_RAZAO_SOCIAL"])
    make_xlsx(tmp_path / "RAW_HAP_TB_PLANO_SINTETICO.xlsx", ["CD_PLANO", "NM_PLANO"])
    make_xlsx(tmp_path / "RAW_HAP_TB_PRECO_PLANO_SINTETICO.xlsx", ["CD_TABELA", "CD_PLANO", "VL_MENSALIDADE"])
    return tmp_path


@pytest.fixture
def stack(data_dir):
    catalog = Catalog(data_dir); catalog.load(strict=True)
    relationships = RelationshipEngine(catalog); relationships.infer()
    return catalog, relationships, SQLGenerator(catalog, relationships)
