from __future__ import annotations

import logging
import os
import re
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .catalog import Catalog
from .column_knowledge import ColumnKnowledge
from .exceptions import DataEngineeringMCPError
from .models import FilterCondition, RelationshipAuthority, SqlGenerationRequest
from .relationships import RelationshipEngine
from .sql_explainer import explain_sql as explain_sql_text
from .sql_generator import SQLGenerator

logging.basicConfig(stream=sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
DATA_DIR = Path(os.getenv("DATA_ENGINEERING_MCP_DATA_DIR", Path.cwd() / "data"))
RELATIONSHIPS_METADATA = Path(os.getenv("DATA_ENGINEERING_MCP_RELATIONSHIPS_FILE", Path.cwd() / "metadata" / "relationships.json"))
COLUMN_DICTIONARY = Path(os.getenv("DATA_ENGINEERING_MCP_COLUMN_DICTIONARY_FILE", DATA_DIR / ".mcp_column_dictionary.json"))
COLUMN_PROFILES = Path(os.getenv("DATA_ENGINEERING_MCP_COLUMN_PROFILES_FILE", DATA_DIR / ".mcp_column_profiles.json"))
catalog = Catalog(DATA_DIR)
relationships = RelationshipEngine(catalog, RELATIONSHIPS_METADATA)
catalog.load(); relationships.infer()
generator = SQLGenerator(catalog, relationships)
column_knowledge = ColumnKnowledge(catalog, COLUMN_DICTIONARY, COLUMN_PROFILES)

mcp = MCPServer(name="data-engineering-mcp", version="0.2.0",
    instructions=(
        "Atenda pedidos de engenharia de dados em linguagem natural, preferencialmente em português. "
        "Use o catálogo e o dicionário para resolver tabelas, colunas e sinônimos antes de gerar SQL. "
        "Consulte perfis locais quando eles ajudarem a esclarecer o significado de uma coluna. "
        "Se faltar uma decisão que possa alterar o resultado, pergunte ao usuário em vez de adivinhar. "
        "Use gerar_sql somente com tabelas, colunas, filtros e grão identificados. "
        "Para otimizar SQL colado ou gerado, explique a consulta, consulte revisar_sql e proponha uma versão "
        "com alterações justificadas, preservando filtros, agregações e grão. Não afirme ganho de desempenho "
        "comprovado: o SQL nunca é executado e o MCP não acessa Oracle. "
        "Nunca chame perfil_colunas com incluir_amostras=true sem autorização explícita do usuário. "
        "Só registre uma definição por ensinar_coluna quando o usuário a fornecer ou confirmar."
    ))

@mcp.tool(description="Lista as tabelas lógicas locais; use para descobrir fontes disponíveis para um pedido em linguagem natural.")
def listar_tabelas() -> list[str]: return catalog.list_tables()


@mcp.tool(description="Mostra cabeçalhos, chaves e significados confirmados; descrições ausentes aparecem como desconhecidas.")
def descrever_tabela(tabela: str) -> dict:
    table = catalog.get_table(tabela)
    return table.model_dump() | {
        "column_count": table.column_count,
        "keys": [key.model_dump(mode="json") for key in relationships.keys_for_table(table.name)],
        "column_knowledge": {item.name: column_knowledge.definition(table.name, item.name) for item in table.columns},
    }


@mcp.tool(description="Busca uma coluna exata no catálogo, sem diferenciar maiúsculas/minúsculas.")
def buscar_coluna(coluna: str) -> list[str]: return catalog.find_column(coluna)


@mcp.tool(description="Busca parcial case-insensitive no nome das tabelas.")
def buscar_tabelas(termo: str) -> list[str]: return catalog.search_tables(termo)


@mcp.tool(description="Retorna os significados confirmados e um perfil agregado local da coluna. Não inclui valores de exemplo.")
def entender_coluna(tabela: str, coluna: str) -> dict:
    table = catalog.get_table(tabela)
    name = coluna.strip().upper()
    if name not in {item.name for item in table.columns}:
        raise ToolError(f"Coluna inexistente em {table.name}: {coluna}")
    return {
        "table": table.name,
        "column": name,
        "knowledge": column_knowledge.definition(table.name, name),
        "profile": column_knowledge.profile(table.name, name, include_samples=False),
    }


@mcp.tool(description="Calcula ou consulta perfis agregados locais. Só use incluir_amostras=true após autorização explícita do usuário; exemplos não são persistidos.")
def perfil_colunas(tabela: str, colunas: list[str] | None = None, incluir_amostras: bool = False) -> dict:
    table = catalog.get_table(tabela)
    selected = [column.strip().upper() for column in colunas] if colunas else [item.name for item in table.columns]
    profiles = {}
    for column in selected:
        try:
            result = column_knowledge.profile(table.name, column, include_samples=incluir_amostras)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        profiles.update(result["columns"])
    return {
        "table": table.name,
        "row_count": result["row_count"] if selected else 0,
        "columns": profiles,
        "raw_values_included": bool(incluir_amostras),
        "notice": "Perfis são calculados nos XLSX locais; valores de exemplo só aparecem com autorização explícita.",
    }


@mcp.tool(description="Ensina ou corrige uma definição confirmada de coluna. Chame somente com definição fornecida ou confirmada pelo usuário.")
def ensinar_coluna(tabela: str, coluna: str, definicao: str, sinonimos: list[str] | None = None) -> dict:
    try:
        return {
            "table": catalog.get_table(tabela).name,
            "column": coluna.strip().upper(),
            "knowledge": column_knowledge.teach(tabela, coluna, definicao, sinonimos),
        }
    except DataEngineeringMCPError as exc:
        raise ToolError(str(exc)) from exc
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(description="Retorna relacionamentos candidatos com autoridade, fonte, decisão e conflitos.")
def inferir_relacionamentos() -> list[dict]: return [r.model_dump(mode="json") for r in relationships.candidates]


@mcp.tool(description="Encontra caminhos candidatos entre duas tabelas; caminhos não aprovados não autorizam JOIN.")
def encontrar_caminho(tabela_origem: str, tabela_destino: str) -> list[dict]: return [p.model_dump(mode="json") for p in relationships.find_paths(tabela_origem, tabela_destino)]


@mcp.tool(description="Revarre XLSX, detecta mudanças de schema e recalcula relacionamentos. Perfis são atualizados sob demanda quando a tabela é consultada.")
def atualizar_catalogo() -> dict:
    old = {(r.source_table, tuple(r.source_columns or []), r.target_table, tuple(r.target_columns or [])) for r in relationships.candidates}
    change = catalog.load(); relationships.infer()
    new = {(r.source_table, tuple(r.source_columns or []), r.target_table, tuple(r.target_columns or [])) for r in relationships.candidates}
    change.new_relationships = len(new - old)
    return change.model_dump(mode="json")


@mcp.tool(description="Informa estatísticas e timestamp do catálogo.")
def status_catalogo() -> dict: return catalog.status(len(relationships.candidates)).model_dump(mode="json")


@mcp.tool(description="Gera SELECT Oracle parametrizado a partir de uma intenção estruturada; não executa SQL.")
def gerar_sql(tabelas: list[str], colunas: list[str] | None = None, filtros: list[FilterCondition] | None = None, permitir_baixa_confianca: bool = False, grain: list[str] | None = None) -> dict:
    try:
        return generator.generate(SqlGenerationRequest(tables=tabelas, columns=colunas, filters=filtros, allow_low_confidence=permitir_baixa_confianca, grain=grain)).model_dump(mode="json")
    except DataEngineeringMCPError as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(description="Gera SELECT Oracle simples de uma tabela, sem executar SQL.")
def gerar_select(tabela: str, colunas: list[str] | None = None) -> dict: return generator.generate_select(tabela, colunas).model_dump(mode="json")


@mcp.tool(description="Descreve um JOIN candidato e informa se seu uso automático está permitido ou bloqueado.")
def gerar_join(tabela_origem: str, tabela_destino: str) -> dict:
    source = catalog.get_table(tabela_origem).name
    rel = relationships.direct(source, catalog.get_table(tabela_destino).name)
    result = rel.model_dump(mode="json")
    result["grain_preservation"] = relationships.grain_preservation(rel, source)
    allowed = rel.authority == RelationshipAuthority.APPROVED and not rel.conflicts
    result |= {"automatic_join": "ALLOWED" if allowed else "BLOCKED", "automatic_join_allowed": allowed}
    if allowed:
        if source == rel.source_table:
            target_table = rel.target_table
            target_columns, source_columns = rel.target_columns or [], rel.source_columns or []
        else:
            target_table = rel.source_table
            target_columns, source_columns = rel.source_columns or [], rel.target_columns or []
        predicates = [
            f"{target_table}.{target_column} = {source}.{source_column}"
            for target_column, source_column in zip(target_columns, source_columns)
        ]
        result["sql_sugerido"] = f"LEFT JOIN {target_table} ON " + " AND ".join(predicates)
    else:
        reasons = []
        if rel.authority != RelationshipAuthority.APPROVED:
            reasons.append(f"authority={rel.authority.value if rel.authority is not None else 'ABSENT'}")
        if rel.conflicts:
            reasons.append(f"conflicts={'; '.join(rel.conflicts)}")
        result["blocked_reason"] = (
            f"automatic JOIN = BLOCKED ({', '.join(reasons)}); "
            "requer homologação HUMAN como APPROVED e ausência de conflitos"
        )
    return result


@mcp.tool(description="Explica conservadoramente uma consulta SELECT/WITH sem executá-la.")
def explicar_sql(sql: str) -> dict: return explain_sql_text(sql)


@mcp.tool(description="Analisa SELECT/WITH com verificações estáticas conservadoras; não reescreve nem comprova desempenho.")
def revisar_sql(sql: str) -> dict:
    analysis = explain_sql_text(sql)
    findings = []
    clean = re.sub(r"--.*?$|/\*.*?\*/", " ", sql, flags=re.M | re.S)
    if re.search(r"\bSELECT\s+(?:DISTINCT\s+)?\*", clean, re.I):
        findings.append({
            "code": "SELECT_STAR",
            "severity": "REVIEW",
            "message": "Considere selecionar somente as colunas necessárias; isso melhora clareza e pode reduzir dados lidos.",
        })
    if re.search(r"\bLIKE\s+(['\"])%", clean, re.I):
        findings.append({
            "code": "LEADING_WILDCARD",
            "severity": "REVIEW",
            "message": "O padrão LIKE começa com curinga; isso pode limitar o uso de índices, mas depende do plano e dos índices no Oracle.",
        })
    return {
        "analysis": analysis,
        "findings": findings,
        "rewrite_performed": False,
        "performance_verified": False,
        "notice": "Verificação estática sem acesso ao banco; valide qualquer reescrita antes de utilizá-la.",
    }


def main() -> None:
    logger.info("Iniciando data-engineering-mcp com %d tabelas", len(catalog.tables))
    mcp.run(transport="stdio")


if __name__ == "__main__": main()
