from datetime import date

import pytest
from mcp import Client

from data_engineering_mcp import server
from data_engineering_mcp.models import RelationshipAuthority, RelationshipDecision


def _use_stack(monkeypatch, stack):
    catalog, relationships, generator = stack
    monkeypatch.setattr(server, "catalog", catalog)
    monkeypatch.setattr(server, "relationships", relationships)
    monkeypatch.setattr(server, "generator", generator)
    return catalog, relationships, generator


def _approve_direct(relationships, source, target):
    relationship = relationships.direct(source, target)
    approved = relationship.model_copy(update={
        "authority": RelationshipAuthority.APPROVED,
        "decision": RelationshipDecision(
            id="G2-SPEC-009-TEST",
            date=date(2026, 9, 17),
            decided_by="HUMAN/Product Owner",
        ),
    })
    relationships.candidates = [
        approved if candidate is relationship else candidate
        for candidate in relationships.candidates
    ]


@pytest.mark.asyncio
async def test_gerar_sql_block_is_readable_at_mcp_boundary(stack, monkeypatch):
    _use_stack(monkeypatch, stack)

    async with Client(server.mcp) as client:
        result = await client.call_tool("gerar_sql", {
            "tabelas": ["RAW_HAP_TB_PESSOA", "RAW_HAP_TB_USUARIO"],
            "colunas": ["RAW_HAP_TB_PESSOA.NM_PESSOA_RAZAO_SOCIAL", "RAW_HAP_TB_USUARIO.CD_USUARIO"],
        })

    text = " ".join(block.text for block in result.content if hasattr(block, "text"))
    assert result.is_error is True
    assert "autoridade INFERRED" in text
    assert "RAW_HAP_TB_PESSOA.CD_PESSOA" in text
    assert "RAW_HAP_TB_USUARIO.CD_PESSOA" in text
    assert "homologação como APPROVED" in text
    assert "Error executing tool gerar_sql" in text
    assert "Internal error" not in text
    assert "SELECT" not in text


@pytest.mark.asyncio
async def test_unexpected_gerar_sql_error_remains_generic(stack, monkeypatch):
    *_, generator = _use_stack(monkeypatch, stack)

    def crash(_request):
        raise RuntimeError("sensitive unexpected failure")

    monkeypatch.setattr(generator, "generate", crash)
    async with Client(server.mcp) as client:
        result = await client.call_tool("gerar_sql", {"tabelas": ["RAW_HAP_TB_PESSOA"]})

    text = " ".join(block.text for block in result.content if hasattr(block, "text"))
    assert result.is_error is True
    assert "Error executing tool gerar_sql" in text
    assert "sensitive unexpected failure" not in text


def test_gerar_join_blocks_inferred_without_sql(stack, monkeypatch):
    _use_stack(monkeypatch, stack)

    result = server.gerar_join("RAW_HAP_TB_PESSOA", "RAW_HAP_TB_USUARIO")

    assert result["authority"] == "INFERRED"
    assert result["conflicts"] == []
    assert result["automatic_join"] == "BLOCKED"
    assert result["automatic_join_allowed"] is False
    assert "automatic JOIN = BLOCKED" in result["blocked_reason"]
    assert "sql_sugerido" not in result
    assert result["grain_preservation"]["status"] == "BLOCKED"
    assert result["grain_preservation"]["cardinality"] == "UNKNOWN"


def test_gerar_join_allows_only_approved_without_conflicts(stack, monkeypatch):
    _, relationships, _ = _use_stack(monkeypatch, stack)
    _approve_direct(relationships, "RAW_HAP_TB_PESSOA", "RAW_HAP_TB_USUARIO")

    result = server.gerar_join("RAW_HAP_TB_PESSOA", "RAW_HAP_TB_USUARIO")

    assert result["authority"] == "APPROVED"
    assert result["automatic_join"] == "ALLOWED"
    assert result["automatic_join_allowed"] is True
    assert result["sql_sugerido"].startswith("LEFT JOIN")
    assert "blocked_reason" not in result
    assert result["grain_preservation"]["status"] == "BLOCKED"


def test_descrever_tabela_exposes_keys_without_inventing_them(stack, monkeypatch):
    _use_stack(monkeypatch, stack)
    result = server.descrever_tabela("RAW_HAP_TB_PESSOA")
    assert result["keys"] == []


@pytest.mark.asyncio
async def test_single_table_and_exact_tool_count_are_preserved(stack, monkeypatch):
    _use_stack(monkeypatch, stack)

    async with Client(server.mcp) as client:
        tools = await client.list_tools()
        result = await client.call_tool("gerar_sql", {
            "tabelas": ["RAW_HAP_TB_PESSOA"],
            "colunas": ["NM_PESSOA_RAZAO_SOCIAL"],
        })

    assert len(tools.tools) == 12
    assert result.is_error is False
    text = " ".join(block.text for block in result.content if hasattr(block, "text"))
    assert "SELECT" in text
    assert "LEFT JOIN" not in text
