from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

from .catalog import Catalog
from .models import FilterCondition, SqlGenerationRequest
from .relationships import RelationshipEngine
from .sql_explainer import explain_sql as explain_sql_text
from .sql_generator import SQLGenerator

logging.basicConfig(stream=sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
DATA_DIR = Path(os.getenv("DATA_ENGINEERING_MCP_DATA_DIR", Path.cwd() / "data"))
catalog = Catalog(DATA_DIR)
relationships = RelationshipEngine(catalog)
catalog.load(); relationships.infer()
generator = SQLGenerator(catalog, relationships)

mcp = MCPServer(name="data-engineering-mcp", version="0.1.0",
    instructions="Catálogo local de XLSX e geração segura de SQL Oracle SELECT. Não acessa bancos nem executa SQL.")


@mcp.tool(description="Lista deterministicamente as tabelas lógicas do catálogo local.")
def listar_tabelas() -> list[str]: return catalog.list_tables()


@mcp.tool(description="Descreve arquivo, aba e cabeçalhos de uma tabela.")
def descrever_tabela(tabela: str) -> dict: return catalog.get_table(tabela).model_dump() | {"column_count": catalog.get_table(tabela).column_count}


@mcp.tool(description="Busca uma coluna exata, sem diferenciar maiúsculas/minúsculas.")
def buscar_coluna(coluna: str) -> list[str]: return catalog.find_column(coluna)


@mcp.tool(description="Busca parcial case-insensitive no nome das tabelas.")
def buscar_tabelas(termo: str) -> list[str]: return catalog.search_tables(termo)


@mcp.tool(description="Retorna relacionamentos candidatos inferidos somente por metadados.")
def inferir_relacionamentos() -> list[dict]: return [r.model_dump(mode="json") for r in relationships.candidates]


@mcp.tool(description="Encontra os melhores caminhos de relacionamentos candidatos com confiança MEDIUM ou HIGH.")
def encontrar_caminho(tabela_origem: str, tabela_destino: str) -> list[dict]: return [p.model_dump(mode="json") for p in relationships.find_paths(tabela_origem, tabela_destino)]


@mcp.tool(description="Revarre XLSX, detecta mudanças de schema e recalcula relacionamentos.")
def atualizar_catalogo() -> dict:
    old = {(r.source_table, r.source_column, r.target_table, r.target_column) for r in relationships.candidates}
    change = catalog.load(); relationships.infer()
    new = {(r.source_table, r.source_column, r.target_table, r.target_column) for r in relationships.candidates}
    change.new_relationships = len(new - old)
    return change.model_dump(mode="json")


@mcp.tool(description="Informa estatísticas e timestamp do catálogo.")
def status_catalogo() -> dict: return catalog.status(len(relationships.candidates)).model_dump(mode="json")


@mcp.tool(description="Gera SELECT Oracle estrutural, parametrizado e sem executar SQL.")
def gerar_sql(tabelas: list[str], colunas: list[str] | None = None, filtros: list[FilterCondition] | None = None, permitir_baixa_confianca: bool = False) -> dict:
    return generator.generate(SqlGenerationRequest(tables=tabelas, columns=colunas, filters=filtros, allow_low_confidence=permitir_baixa_confianca)).model_dump(mode="json")


@mcp.tool(description="Gera SELECT Oracle simples de uma tabela, sem executar SQL.")
def gerar_select(tabela: str, colunas: list[str] | None = None) -> dict: return generator.generate_select(tabela, colunas).model_dump(mode="json")


@mcp.tool(description="Propõe JOIN candidato direto entre duas tabelas, sem afirmar chave estrangeira.")
def gerar_join(tabela_origem: str, tabela_destino: str) -> dict:
    rel = relationships.direct(catalog.get_table(tabela_origem).name, catalog.get_table(tabela_destino).name)
    return rel.model_dump(mode="json") | {"sql_sugerido": f"LEFT JOIN {rel.target_table} ON {rel.target_table}.{rel.target_column} = {rel.source_table}.{rel.source_column}"}


@mcp.tool(description="Explica conservadoramente uma consulta SELECT/WITH sem executá-la.")
def explicar_sql(sql: str) -> dict: return explain_sql_text(sql)


def main() -> None:
    logger.info("Iniciando data-engineering-mcp com %d tabelas", len(catalog.tables))
    mcp.run(transport="stdio")


if __name__ == "__main__": main()
