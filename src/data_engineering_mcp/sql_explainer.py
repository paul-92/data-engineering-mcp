import re

from .exceptions import ForbiddenSQLOperationError

FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|MERGE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b", re.I)


def explain_sql(sql: str) -> dict:
    clean = re.sub(r"--.*?$|/\*.*?\*/", " ", sql, flags=re.M | re.S).strip()
    if FORBIDDEN.search(clean) or not re.match(r"^(SELECT|WITH)\b", clean, re.I):
        raise ForbiddenSQLOperationError("Somente consultas SELECT/WITH podem ser explicadas")
    tables = re.findall(r"\b(?:FROM|JOIN)\s+([A-Z][\w$#.]*)", clean, re.I)
    aliases = dict(re.findall(r"\b(?:FROM|JOIN)\s+([A-Z][\w$#.]*)\s+(?!ON\b|WHERE\b|JOIN\b)([A-Z][\w$#]*)", clean, re.I))
    joins = re.findall(r"\b(?:LEFT|RIGHT|FULL|INNER|CROSS)?\s*JOIN\s+[^\n]+(?:\n|\s)+ON\s+([^\n]+)", clean, re.I)
    where = re.search(r"\bWHERE\s+(.+?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|$)", clean, re.I | re.S)
    select = re.search(r"\bSELECT\s+(.+?)\s+FROM\b", clean, re.I | re.S)
    return {"tabelas": tables, "aliases": aliases, "colunas_selecionadas": [x.strip() for x in select.group(1).split(",")] if select else [],
        "joins": joins, "filtros": where.group(1).strip() if where else None, "possui_cte": bool(re.match(r"^WITH\b", clean, re.I)),
        "possui_agregacao": bool(re.search(r"\b(COUNT|SUM|AVG|MIN|MAX)\s*\(", clean, re.I)),
        "observacao": "Análise sintática conservadora; não comprova validade semântica nem executa SQL."}
