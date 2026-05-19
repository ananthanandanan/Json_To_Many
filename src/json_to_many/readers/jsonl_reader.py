from __future__ import annotations

import io
import json
import os
import warnings
from typing import Any

from ..utils.constants import DEFAULT_ENCODING

JSONL_READER_OPTIONS = frozenset(
    {
        "strict",
        "encoding",
    }
)


def _open_source(source: Any, encoding: str) -> io.StringIO:
    if hasattr(source, "read"):
        text = source.read()
        if isinstance(text, bytes):
            text = text.decode(encoding)
        return io.StringIO(text)
    if isinstance(source, os.PathLike):
        with open(source, "r", encoding=encoding) as f:
            return io.StringIO(f.read())
    if isinstance(source, str):
        if os.path.exists(source):
            with open(source, "r", encoding=encoding) as f:
                return io.StringIO(f.read())
        return io.StringIO(source)
    raise TypeError(f"JSONL reader cannot read from {type(source).__name__}")


def read_jsonl(
    source: Any,
    *,
    strict: bool = False,
    encoding: str = DEFAULT_ENCODING,
) -> list[dict]:
    """Read a JSONL source (one JSON value per line) into a list of records.

    `source` may be a file path, a JSONL string, or a text/binary stream.
    Empty and whitespace-only lines are skipped. When `strict=False` (default),
    lines that fail to parse are emitted as `UserWarning` and skipped; with
    `strict=True` the first bad line raises `ValueError`.
    """
    buf = _open_source(source, encoding)
    records: list[dict] = []
    for line_no, raw in enumerate(buf, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            if strict:
                raise ValueError(f"jsonl_reader: line {line_no} — {exc.msg}") from exc
            warnings.warn(
                f"jsonl_reader: line {line_no} skipped — {exc.msg}",
                stacklevel=2,
            )
    return records
