from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from .catalog import Catalog
from .exceptions import DataEngineeringMCPError
from .models import FilterCondition, RelationshipAuthority, SqlGenerationRequest
from .relationships import RelationshipEngine
from .sql_explainer import explain_sql as explain_sql_text
from .sql_generator import SQLGenerator

logging.basicConfig(stream=sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
DATA_DIR = Path(os.getenv("DATA_ENGINEERING_MCP_DATA_DIR", Path.cwd() / "data"))
RELATIONSHIPS_METADATA = Path(os.getenv("DATA_ENGINEERING_MCP_RELATIONSHIPS_FILE", Path.cwd() / "metadata" / "relationships.json"))
catalog = Catalog(DATA_DIR)
relationships = RelationshipEngine(catalog, RELATIONSHIPS_METADATA)
catalog.load(); relationships.infer()
generator = SQLGenerator(catalog, relationships)

mcp = MCPServer(name="data-engineering-mcp", version="0.1.0",
    instructions="Catálogo local de XLSX e geração segura de SQL Oracle SELECT. Não acessa bancos nem executa SQL.")


@mcp.tool(description="Lista deterministicamente as tabelas lógicas do catálogo local.")
def listar_tabelas() -> list[str]: return catalog.list_tables()


@mcp.tool(description="Descreve arquivo, aba, cabeçalhos e chaves explícitas de uma tabela.")
def descrever_tabela(tabela: str) -> dict:
    table = catalog.get_table(tabela)
    return table.model_dump() | {
        "column_count": table.column_count,
        "keys": [key.model_dump(mode="json") for key in relationships.keys_for_table(table.name)],
    }


@mcp.tool(description="Busca uma coluna exata, sem diferenciar maiúsculas/minúsculas.")
def buscar_coluna(coluna: str) -> list[str]: return catalog.find_column(coluna)


@mcp.tool(description="Busca parcial case-insensitive no nome das tabelas.")
def buscar_tabelas(termo: str) -> list[str]: return catalog.search_tables(termo)


@mcp.tool(description="Retorna relacionamentos candidatos com autoridade, fonte, decisão e conflitos.")
def inferir_relacionamentos() -> list[dict]: return [r.model_dump(mode="json") for r in relationships.candidates]


@mcp.tool(description="Encontra os melhores caminhos de relacionamentos candidatos com confiança MEDIUM ou HIGH.")
def encontrar_caminho(tabela_origem: str, tabela_destino: str) -> list[dict]: return [p.model_dump(mode="json") for p in relationships.find_paths(tabela_origem, tabela_destino)]


@mcp.tool(description="Revarre XLSX, detecta mudanças de schema e recalcula relacionamentos.")
def atualizar_catalogo() -> dict:
    old = {(r.source_table, tuple(r.source_columns or []), r.target_table, tuple(r.target_columns or [])) for r in relationships.candidates}
    change = catalog.load(); relationships.infer()
    new = {(r.source_table, tuple(r.source_columns or []), r.target_table, tuple(r.target_columns or [])) for r in relationships.candidates}
    change.new_relationships = len(new - old)
    return change.model_dump(mode="json")


@mcp.tool(description="Informa estatísticas e timestamp do catálogo.")
def status_catalogo() -> dict: return catalog.status(len(relationships.candidates)).model_dump(mode="json")


@mcp.tool(description="Gera SELECT Oracle estrutural, parametrizado e sem executar SQL.")
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


def main() -> None:
    logger.info("Iniciando data-engineering-mcp com %d tabelas", len(catalog.tables))
    mcp.run(transport="stdio")


if __name__ == "__main__": main()
