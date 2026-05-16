from __future__ import annotations

import json
from typing import Any

from ..result import ConversionResult, ConversionStats
from ..utils.constants import DEFAULT_ENCODING
from .base_converter import BaseConverter


class JsonFormatter(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.converted_data: str | None = None

    def converter(self) -> None:
        indent = self.options.get("indent", 2)
        ensure_ascii: bool = self.options.get("ensure_ascii", False)
        sort_keys: bool = self.options.get("sort_keys", False)

        self.converted_data = json.dumps(
            self.data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
        )

        if isinstance(self.data, list):
            rows = len(self.data)
            first = (
                self.data[0] if self.data and isinstance(self.data[0], dict) else None
            )
            fields = len(first) if first else 0
        elif isinstance(self.data, dict):
            rows = 1
            fields = len(self.data)
        else:
            rows = 0
            fields = 0
        self._stats = ConversionStats(rows=rows, fields=fields)

    def save_to_file(self, file_name: str) -> None:
        assert self.converted_data is not None
        encoding = self.options.get("encoding", DEFAULT_ENCODING)
        with open(file_name, "w", encoding=encoding) as f:
            f.write(self.converted_data)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(
            data=self.converted_data, format="json", stats=self._stats
        )
