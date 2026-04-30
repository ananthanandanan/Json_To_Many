from __future__ import annotations

from typing import Any

from ..result import ConversionResult, ConversionStats
from ..utils.constants import DEFAULT_ENCODING
from ..utils.json_utils import flatten_json
from ..utils.schema import analyze_schema
from .base_converter import BaseConverter

_SCHEMA_TO_SQL: dict[str, str] = {
    "int": "INTEGER",
    "float": "REAL",
    "bool": "INTEGER",
    "str": "TEXT",
    "null": "TEXT",
    "mixed": "TEXT",
    "list": "TEXT",
    "object": "TEXT",
}


def _escape(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


class JsonToSQL(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.converted_data: str | None = None

    def converter(self) -> None:
        table: str = self.options.get("table", "data")
        batch_size: int = self.options.get("batch_size", 500)
        include_create: bool = self.options.get("include_create", False)

        records: list[dict] = (
            [flatten_json(r) for r in self.data]
            if isinstance(self.data, list)
            else [flatten_json(self.data)]
        )

        columns: list[str] = list(dict.fromkeys(k for r in records for k in r))
        col_list = ", ".join(columns)

        parts: list[str] = []

        if include_create:
            schema = analyze_schema(self.data)
            type_map = {f.name: _SCHEMA_TO_SQL.get(f.type, "TEXT") for f in schema.fields}
            col_defs = ",\n  ".join(
                f"{col} {type_map.get(col, 'TEXT')}" for col in columns
            )
            parts.append(f"CREATE TABLE IF NOT EXISTS {table} (\n  {col_defs}\n);")

        for batch_start in range(0, len(records), batch_size):
            batch = records[batch_start : batch_start + batch_size]
            value_rows = []
            for row in batch:
                vals = ", ".join(_escape(row.get(col)) for col in columns)
                value_rows.append(f"  ({vals})")
            parts.append(
                f"INSERT INTO {table} ({col_list}) VALUES\n"
                + ",\n".join(value_rows)
                + ";"
            )

        self.converted_data = "\n\n".join(parts)
        self._stats = ConversionStats(rows=len(records), fields=len(columns))

    def save_to_file(self, file_name: str) -> None:
        assert self.converted_data is not None
        with open(file_name, "w", encoding=DEFAULT_ENCODING) as f:
            f.write(self.converted_data)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(data=self.converted_data, format="sql", stats=self._stats)
