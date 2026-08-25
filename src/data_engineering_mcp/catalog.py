from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook

from .exceptions import MissingHeaderError, NoValidWorksheetError, TableNotFoundError
from .models import CatalogChange, CatalogStatus, ColumnSchema, TableSchema

logger = logging.getLogger(__name__)


def normalize_table_name(filename: str) -> str:
    name = Path(filename).stem
    name = re.sub(r"^rawzn\.", "", name, flags=re.IGNORECASE)
    name = re.sub(r"_SINTETICO$", "", name, flags=re.IGNORECASE)
    return name.upper()


class Catalog:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.tables: dict[str, TableSchema] = {}
        self.loaded_at = datetime.now(timezone.utc)
        self.errors: list[str] = []

    def load(self, strict: bool = False) -> CatalogChange:
        previous = self.tables
        discovered: dict[str, TableSchema] = {}
        errors: list[str] = []
        self.data_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(self.data_dir.glob("*.xlsx"), key=lambda p: p.name.casefold())
        logger.info("Carregando catálogo de %d arquivos XLSX", len(files))
        for path in files:
            try:
                table = self._read_schema(path)
                if table.name in discovered:
                    raise ValueError(f"Nome lógico duplicado: {table.name}")
                discovered[table.name] = table
            except Exception as exc:
                logger.error("Falha ao ler %s: %s", path.name, exc)
                if strict:
                    raise
                errors.append(f"{path.name}: {exc}")
        now = datetime.now(timezone.utc)
        old_names, new_names = set(previous), set(discovered)
        changed = sorted(
            name for name in old_names & new_names
            if [c.name for c in previous[name].columns] != [c.name for c in discovered[name].columns]
        )
        self.tables, self.loaded_at, self.errors = discovered, now, errors
        return CatalogChange(
            previous_table_count=len(previous), current_table_count=len(discovered),
            added=sorted(new_names - old_names), removed=sorted(old_names - new_names),
            schemas_changed=changed, new_relationships=0, loaded_at=now, errors=errors,
        )

    def _read_schema(self, path: Path) -> TableSchema:
        try:
            workbook = load_workbook(path, read_only=True, data_only=True)
        except Exception as exc:
            raise NoValidWorksheetError(f"Arquivo XLSX inválido: {path.name}") from exc
        try:
            usable = [ws for ws in workbook.worksheets if ws.title.casefold() != "sql"]
            if not usable:
                raise NoValidWorksheetError(f"Workbook {path.name} não possui aba válida")
            for worksheet in usable:
                row = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
                headers = [str(value).strip().upper() for value in row if value is not None and str(value).strip()]
                if headers:
                    if len(headers) != len(set(headers)):
                        raise MissingHeaderError(f"Cabeçalhos duplicados em {path.name}/{worksheet.title}")
                    return TableSchema(
                        name=normalize_table_name(path.name), source_file=path.name, worksheet=worksheet.title,
                        columns=[ColumnSchema(name=name, position=i) for i, name in enumerate(headers, 1)],
                    )
            raise MissingHeaderError(f"Workbook {path.name} não possui cabeçalho")
        finally:
            workbook.close()

    def list_tables(self) -> list[str]:
        return sorted(self.tables)

    def get_table(self, name: str) -> TableSchema:
        key = name.upper()
        if key not in self.tables:
            raise TableNotFoundError(f"Tabela inexistente: {name}. Disponíveis: {', '.join(self.list_tables()) or 'nenhuma'}")
        return self.tables[key]

    def find_column(self, column: str) -> list[str]:
        needle = column.upper()
        return sorted(f"{table.name}.{col.name}" for table in self.tables.values() for col in table.columns if col.name == needle)

    def search_tables(self, term: str) -> list[str]:
        needle = term.casefold()
        return [name for name in self.list_tables() if needle in name.casefold()]

    def status(self, relationship_count: int = 0) -> CatalogStatus:
        return CatalogStatus(file_count=len(self.tables), table_count=len(self.tables),
            total_columns=sum(t.column_count for t in self.tables.values()), loaded_at=self.loaded_at,
            tables=self.list_tables(), relationship_count=relationship_count)
