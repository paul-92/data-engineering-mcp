from __future__ import annotations

import json
import os
import tempfile
from collections import Counter
from datetime import date, datetime, timezone
from numbers import Number
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from .catalog import Catalog


class ColumnKnowledge:
    """Persiste definições humanas e perfis agregados de XLSX locais."""

    VERSION = 1
    SAMPLE_LIMIT = 5

    def __init__(self, catalog: Catalog, dictionary_path: Path | str, profiles_path: Path | str):
        self.catalog = catalog
        self.dictionary_path = Path(dictionary_path)
        self.profiles_path = Path(profiles_path)
        self._dictionary = self._read_json(self.dictionary_path, {"version": self.VERSION, "columns": {}})
        self._profiles = self._read_json(self.profiles_path, {"version": self.VERSION, "tables": {}})
        self._validate_document(self._dictionary, "dicionário", "columns")
        self._validate_document(self._profiles, "perfis", "tables")

    @staticmethod
    def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return default
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Não foi possível ler {path}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Documento inválido em {path}: esperado objeto JSON")
        return value

    @staticmethod
    def _validate_document(document: dict[str, Any], label: str, key: str) -> None:
        if document.get("version") != ColumnKnowledge.VERSION or not isinstance(document.get(key), dict):
            raise ValueError(f"Formato inválido para {label}; esperado version={ColumnKnowledge.VERSION} e '{key}'")

    @staticmethod
    def _atomic_write(path: Path, document: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
                temp_name = stream.name
                json.dump(document, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def identity(table: str, column: str) -> str:
        return f"{table.strip().upper()}.{column.strip().upper()}"

    def definition(self, table: str, column: str) -> dict[str, Any]:
        entry = self._dictionary["columns"].get(self.identity(table, column))
        if entry is None:
            return {"status": "UNKNOWN", "definition": None, "synonyms": []}
        return dict(entry)

    def definitions_for_table(self, table: str) -> dict[str, dict[str, Any]]:
        prefix = f"{table.strip().upper()}."
        return {
            key[len(prefix):]: dict(value)
            for key, value in sorted(self._dictionary["columns"].items())
            if key.startswith(prefix)
        }

    def teach(self, table: str, column: str, definition: str, synonyms: list[str] | None = None) -> dict[str, Any]:
        table_schema = self.catalog.get_table(table)
        column_name = column.strip().upper()
        if column_name not in {item.name for item in table_schema.columns}:
            raise ValueError(f"Coluna inexistente em {table_schema.name}: {column}")
        clean_definition = " ".join(definition.split())
        if not clean_definition:
            raise ValueError("A definição não pode ficar vazia")
        clean_synonyms = sorted({item.strip() for item in (synonyms or []) if item and item.strip()}, key=str.casefold)
        entry = {
            "status": "CONFIRMED",
            "definition": clean_definition,
            "synonyms": clean_synonyms,
            "source": "HUMAN",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._dictionary["columns"][self.identity(table_schema.name, column_name)] = entry
        self._atomic_write(self.dictionary_path, self._dictionary)
        return dict(entry)

    def _fingerprint(self, table_name: str) -> dict[str, Any]:
        table = self.catalog.get_table(table_name)
        path = self.catalog.data_dir / table.source_file
        stat = path.stat()
        return {
            "source_file": table.source_file,
            "worksheet": table.worksheet,
            "size": stat.st_size,
            "modified_ns": stat.st_mtime_ns,
            "columns": [column.name for column in table.columns],
        }

    def profile(self, table_name: str, column_name: str | None = None, include_samples: bool = False) -> dict[str, Any]:
        table = self.catalog.get_table(table_name)
        all_columns = {column.name for column in table.columns}\n        selected = set(all_columns)
        if column_name is not None:
            column_name = column_name.strip().upper()
            if column_name not in selected:
                raise ValueError(f"Coluna inexistente em {table.name}: {column_name}")
            selected &= {column_name}

        fingerprint = self._fingerprint(table.name)
        cached = self._profiles["tables"].get(table.name)
        if not include_samples and cached and cached.get("fingerprint") == fingerprint:
            metrics = cached["columns"]
            return {
                "table": table.name,
                "source_file": table.source_file,
                "worksheet": table.worksheet,
                "row_count": cached["row_count"],
                "columns": {name: metrics[name] for name in sorted(selected) if name in metrics},
                "cached": True,
                "raw_values_included": False,
            }

        path = self.catalog.data_dir / table.source_file
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            worksheet = workbook[table.worksheet]
            headers = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
            header_positions = {str(value).strip().upper(): index for index, value in enumerate(headers) if value is not None and str(value).strip()}
            column_names = sorted(all_columns if not include_samples else selected)
            stats = {
                name: {"non_empty": 0, "empty": 0, "types": Counter(), "samples": [], "_seen": set()}
                for name in column_names
            }
            row_count = 0
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if not any(value is not None and str(value).strip() for value in row):
                    continue
                row_count += 1
                for name in column_names:
                    index = header_positions.get(name)
                    value = row[index] if index is not None and index < len(row) else None
                    item = stats[name]
                    if value is None or (isinstance(value, str) and not value.strip()):
                        item["empty"] += 1
                        continue
                    item["non_empty"] += 1
                    if isinstance(value, bool):
                        kind = "boolean"
                    elif isinstance(value, datetime):
                        kind = "datetime"
                    elif isinstance(value, date):
                        kind = "date"
                    elif isinstance(value, Number):
                        kind = "number"
                    else:
                        kind = "text"
                    item["types"][kind] += 1
                    if include_samples and len(item["samples"]) < self.SAMPLE_LIMIT:
                        sample = str(value).strip()
                        if sample and sample not in item["_seen"]:
                            item["_seen"].add(sample)
                            item["samples"].append(sample)
            columns: dict[str, dict[str, Any]] = {}
            for name, item in stats.items():
                non_empty = item["non_empty"]
                type_counts = dict(item["types"])
                inferred = max(type_counts, key=type_counts.get) if type_counts else "unknown"
                columns[name] = {
                    "non_empty": non_empty,
                    "empty": item["empty"],
                    "empty_ratio": round(item["empty"] / row_count, 4) if row_count else 0.0,
                    "type_counts": type_counts,
                    "likely_type": inferred,
                }
                if include_samples:
                    columns[name]["sample_values"] = item["samples"]
        finally:
            workbook.close()

        if not include_samples:
            self._profiles["tables"][table.name] = {
                "fingerprint": fingerprint,
                "row_count": row_count,
                "columns": columns,
                "profiled_at": datetime.now(timezone.utc).isoformat(),
            }
            self._atomic_write(self.profiles_path, self._profiles)

        return {
            "table": table.name,
            "source_file": table.source_file,
            "worksheet": table.worksheet,
            "row_count": row_count,
            "columns": columns,
            "cached": False,
            "raw_values_included": bool(include_samples),
        }
