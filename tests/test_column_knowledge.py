import json
import shutil
import uuid
from pathlib import Path

import pytest
from openpyxl import Workbook

from data_engineering_mcp.catalog import Catalog
from data_engineering_mcp.column_knowledge import ColumnKnowledge


@pytest.fixture
def working_dir():
    root = Path(__file__).resolve().parents[2] / "pytest-column-knowledge-data"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def make_catalog(working_dir: Path) -> Catalog:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Dados"
    sheet.append(["CD_USUARIO", "NM_STATUS"])
    sheet.append([1, "Ativo"])
    sheet.append([2, "Inativo"])
    sheet.append([3, None])
    sheet.append([4, "Ativo"])
    sheet.append([5, "Pendente"])
    sheet.append([6, "Suspenso"])
    sheet.append([7, "Cancelado"])
    workbook.save(working_dir / "RAW_HAP_TB_USUARIO_SINTETICO.xlsx")
    catalog = Catalog(working_dir)
    catalog.load(strict=True)
    return catalog


def make_knowledge(working_dir: Path) -> ColumnKnowledge:
    return ColumnKnowledge(
        make_catalog(working_dir),
        working_dir / "data" / ".mcp_column_dictionary.json",
        working_dir / "data" / ".mcp_column_profiles.json",
    )


def test_teach_persists_human_confirmed_definition_and_synonyms(working_dir):
    knowledge = make_knowledge(working_dir)

    taught = knowledge.teach(
        "raw_hap_tb_usuario",
        "nm_status",
        "  Situação   cadastral do usuário  ",
        ["situação", " status ", "situação", ""],
    )
    reloaded = ColumnKnowledge(
        knowledge.catalog, knowledge.dictionary_path, knowledge.profiles_path
    )

    assert taught["status"] == "CONFIRMED"
    assert taught["definition"] == "Situação cadastral do usuário"
    assert taught["synonyms"] == ["situação", "status"]
    assert taught["source"] == "HUMAN"
    assert reloaded.definition("RAW_HAP_TB_USUARIO", "NM_STATUS")["definition"] == taught["definition"]


def test_teach_rejects_unknown_column_and_blank_definition(working_dir):
    knowledge = make_knowledge(working_dir)

    with pytest.raises(ValueError, match="Coluna inexistente"):
        knowledge.teach("RAW_HAP_TB_USUARIO", "NAO_EXISTE", "Descrição")
    with pytest.raises(ValueError, match="não pode ficar vazia"):
        knowledge.teach("RAW_HAP_TB_USUARIO", "NM_STATUS", "  ")


def test_profile_returns_aggregates_and_caches_without_persisting_values(working_dir):
    knowledge = make_knowledge(working_dir)

    first = knowledge.profile("RAW_HAP_TB_USUARIO", "NM_STATUS")
    second = knowledge.profile("RAW_HAP_TB_USUARIO", "NM_STATUS")
    saved = knowledge.profiles_path.read_text(encoding="utf-8")

    assert first["row_count"] == 7
    assert first["columns"]["NM_STATUS"]["non_empty"] == 6
    assert first["columns"]["NM_STATUS"]["empty"] == 1
    assert first["columns"]["NM_STATUS"]["likely_type"] == "text"
    assert first["raw_values_included"] is False
    assert first["cached"] is False
    assert second["cached"] is True
    assert "Ativo" not in saved
    assert "Suspenso" not in saved


def test_profile_samples_are_limited_and_not_persisted(working_dir):
    knowledge = make_knowledge(working_dir)

    result = knowledge.profile("RAW_HAP_TB_USUARIO", "NM_STATUS", include_samples=True)
    saved_profiles = json.loads(knowledge.profiles_path.read_text(encoding="utf-8")) if knowledge.profiles_path.exists() else {}

    assert result["raw_values_included"] is True
    assert result["columns"]["NM_STATUS"]["sample_values"] == ["Ativo", "Inativo", "Pendente", "Suspenso", "Cancelado"]
    assert len(result["columns"]["NM_STATUS"]["sample_values"]) <= ColumnKnowledge.SAMPLE_LIMIT
    assert saved_profiles.get("tables", {}) == {}


def test_profile_rejects_unknown_column(working_dir):
    knowledge = make_knowledge(working_dir)

    with pytest.raises(ValueError, match="Coluna inexistente"):
        knowledge.profile("RAW_HAP_TB_USUARIO", "NAO_EXISTE")
