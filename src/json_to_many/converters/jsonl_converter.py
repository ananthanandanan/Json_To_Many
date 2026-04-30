from __future__ import annotations

import json
from typing import Any

from ..result import ConversionResult, ConversionStats
from ..utils.constants import DEFAULT_ENCODING
from .base_converter import BaseConverter


class JsonToJSONL(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.converted_data: str | None = None

    def converter(self) -> None:
        records = self.data if isinstance(self.data, list) else [self.data]
        ensure_ascii: bool = self.options.get("ensure_ascii", True)
        self.converted_data = "\n".join(
            json.dumps(r, ensure_ascii=ensure_ascii) for r in records
        )
        self._stats = ConversionStats(rows=len(records))

    def save_to_file(self, file_name: str) -> None:
        assert self.converted_data is not None
        with open(file_name, "w", encoding=DEFAULT_ENCODING) as f:
            f.write(self.converted_data)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(
            data=self.converted_data, format="jsonl", stats=self._stats
        )
