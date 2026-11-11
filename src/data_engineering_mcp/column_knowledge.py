from __future__ import annotations

import hashlib
import hmac
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

    @staticmethod
    def _comparison_key(value: Any, secret: bytes) -> str:
        """Retorna um digest efêmero para comparar sem expor nem persistir valores."""
        if isinstance(value, bool):
            canonical = f"bool:{value}"
        elif isinstance(value, Number):
            canonical = f"number:{value}"
        elif isinstance(value, (datetime, date)):
            canonical = f"{type(value).__name__}:{value.isoformat()}"
        else:
            canonical = f"text:{str(value).strip()}"
        return hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    def _column_frequency(self, table_name: str, column_name: str, secret: bytes) -> dict[str, Any]:
        table = self.catalog.get_table(table_name)
        column = column_name.strip().upper()
        if column not in {item.name for item in table.columns}:
            raise ValueError(f"Coluna inexistente em {table.name}: {column}")
        path = self.catalog.data_dir / table.source_file
        workbook = load_workbook(path, read_only=True, data_only=True)
        frequencies: Counter[str] = Counter()
        empty = row_count = 0
        try:
            worksheet = workbook[table.worksheet]
            headers = next(worksheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
            positions = {str(value).strip().upper(): index for index, value in enumerate(headers) if value is not None and str(value).strip()}
            position = positions.get(column)
            if position is None:
                raise ValueError(f"Cabeçalho não encontrado em {table.name}: {column}")
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if not any(value is not None and str(value).strip() for value in row):
                    continue
                row_count += 1
                value = row[position] if position < len(row) else None
                if value is None or (isinstance(value, str) and not value.strip()):
                    empty += 1
                else:
                    frequencies[self._comparison_key(value, secret)] += 1
        finally:
            workbook.close()
        return {"table": table.name, "column": column, "row_count": row_count, "empty": empty, "frequencies": frequencies}

    def compare_columns(self, left_table: str, left_column: str, right_table: str, right_column: str) -> dict[str, Any]:
        """Compara duas colunas locais; retorna somente contagens, nunca valores de célula."""
        secret = os.urandom(32)
        left = self._column_frequency(left_table, left_column, secret)
        right = self._column_frequency(right_table, right_column, secret)
        left_freq, right_freq = left["frequencies"], right["frequencies"]
        shared = left_freq.keys() & right_freq.keys()
        left_distinct, right_distinct = len(left_freq), len(right_freq)
        return {
            "left": {"table": left["table"], "column": left["column"], "row_count": left["row_count"],
                     "empty": left["empty"], "non_empty": sum(left_freq.values()), "distinct": left_distinct,
                     "duplicate_values": sum(count > 1 for count in left_freq.values()),
                     "duplicate_rows": sum(count - 1 for count in left_freq.values() if count > 1)},
            "right": {"table": right["table"], "column": right["column"], "row_count": right["row_count"],
                      "empty": right["empty"], "non_empty": sum(right_freq.values()), "distinct": right_distinct,
                      "duplicate_values": sum(count > 1 for count in right_freq.values()),
                      "duplicate_rows": sum(count - 1 for count in right_freq.values() if count > 1)},
            "overlap_distinct": len(shared),
            "matching_left_rows": sum(left_freq[key] for key in shared),
            "matching_right_rows": sum(right_freq[key] for key in shared),
            "unmatched_left_rows": sum(count for key, count in left_freq.items() if key not in right_freq),
            "unmatched_right_rows": sum(count for key, count in right_freq.items() if key not in left_freq),
            "potential_inner_join_rows": sum(left_freq[key] * right_freq[key] for key in shared),
            "left_values_matching_multiple_right_rows": sum(left_freq[key] for key in shared if right_freq[key] > 1),
            "raw_values_returned": False,
            "notice": "Contagens exatas calculadas localmente; valores de célula não são retornados nem persistidos.",
        }

    def profile(self, table_name: str, column_name: str | None = None, include_samples: bool = False) -> dict[str, Any]:
        table = self.catalog.get_table(table_name)
        all_columns = {column.name for column in table.columns}
        selected = set(all_columns)
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
            "columns": {name: columns[name] for name in sorted(selected)},
            "cached": False,
            "raw_values_included": bool(include_samples),
        }
