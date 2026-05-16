from __future__ import annotations

import csv
import io
import os
from typing import Any

from ..utils.constants import DEFAULT_ENCODING
from ..utils.type_infer import coerce_string

DEFAULT_NULL_VALUES: tuple[str, ...] = ("", "N/A", "NULL")

CSV_READER_OPTIONS = frozenset(
    {
        "infer_types",
        "null_values",
        "header",
        "nested",
        "flatten_sep",
        "delimiter",
        "quotechar",
        "encoding",
    }
)


def _open_source(source: Any, encoding: str) -> io.StringIO:
    if hasattr(source, "read"):
        text = source.read()
        if isinstance(text, bytes):
            text = text.decode(encoding)
        return io.StringIO(text)
    if isinstance(source, str):
        if os.path.exists(source):
            with open(source, "r", encoding=encoding, newline="") as f:
                return io.StringIO(f.read())
        return io.StringIO(source)
    raise TypeError(f"CSV reader cannot read from {type(source).__name__}")


def _unflatten(flat: dict, sep: str) -> dict:
    out: dict = {}
    for key, value in flat.items():
        if sep not in key:
            out[key] = value
            continue
        parts = key.split(sep)
        cursor = out
        for part in parts[:-1]:
            existing = cursor.get(part)
            if not isinstance(existing, dict):
                existing = {}
                cursor[part] = existing
            cursor = existing
        cursor[parts[-1]] = value
    return out


def read_csv(
    source: Any,
    *,
    infer_types: bool = True,
    null_values: tuple[str, ...] | list[str] = DEFAULT_NULL_VALUES,
    header: bool = True,
    nested: bool = True,
    flatten_sep: str = ".",
    delimiter: str = ",",
    quotechar: str = '"',
    encoding: str = DEFAULT_ENCODING,
) -> list[dict]:
    """Read a CSV source into a list of records.

    `source` may be a file path, a CSV string, or a text/binary stream.
    Type inference is per-cell: each value is coerced independently. `null_values`
    applies regardless of `infer_types`.
    """
    null_tuple = tuple(null_values)
    buf = _open_source(source, encoding)
    rows = list(csv.reader(buf, delimiter=delimiter, quotechar=quotechar))
    if not rows:
        return []

    if header:
        columns = rows[0]
        body = rows[1:]
    else:
        width = max(len(r) for r in rows)
        columns = [f"col_{i}" for i in range(width)]
        body = rows

    records: list[dict] = []
    for raw in body:
        flat: dict = {}
        for col, value in zip(columns, raw):
            if infer_types:
                flat[col] = coerce_string(value, null_tuple)
            else:
                flat[col] = None if value in null_tuple else value
        records.append(_unflatten(flat, flatten_sep) if nested else flat)
    return records
