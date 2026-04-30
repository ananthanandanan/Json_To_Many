import csv
import io
from typing import Any
from .base_converter import BaseConverter
from ..utils.constants import DEFAULT_ENCODING
from ..utils.json_utils import flatten_json
from ..result import ConversionResult, ConversionStats


class JsonToCSV(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.csv_data: list[dict] = []
        self.fieldnames: list[str] = []
        self.converted_data: str | None = None

    def converter(self) -> None:
        if isinstance(self.data, dict):
            self.data = [self.data]
        elif not isinstance(self.data, list):
            raise ValueError(
                "Invalid JSON data: Expected a dictionary or a list of dictionaries."
            )

        self.csv_data = [flatten_json(item) for item in self.data]

        columns: list[str] | None = self.options.get("columns", None)
        if columns is not None:
            self.fieldnames = columns
        else:
            self.fieldnames = self.get_fieldnames(self.csv_data)

        self.converted_data = self.generate_csv_string()
        self._stats = ConversionStats(
            rows=len(self.csv_data), fields=len(self.fieldnames)
        )

    def get_fieldnames(self, data: list[dict]) -> list[str]:
        fieldnames: set[str] = set()
        for item in data:
            fieldnames.update(item.keys())
        return list(fieldnames)

    def generate_csv_string(self) -> str:
        delimiter: str = self.options.get("delimiter", ",")
        quotechar: str = self.options.get("quotechar", '"')
        include_header: bool = self.options.get("include_header", True)
        columns: list[str] | None = self.options.get("columns", None)
        extrasaction = "ignore" if columns is not None else "raise"

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=self.fieldnames,
            delimiter=delimiter,
            quotechar=quotechar,
            extrasaction=extrasaction,
        )
        if include_header:
            writer.writeheader()
        for item in self.csv_data:
            writer.writerow({key: item.get(key, "") for key in self.fieldnames})
        return output.getvalue()

    def save_to_file(self, file_name: str) -> None:
        assert self.converted_data is not None
        encoding = self.options.get("encoding", DEFAULT_ENCODING)
        with open(file_name, "w", newline="", encoding=encoding) as csvfile:
            csvfile.write(self.converted_data)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(
            data=self.converted_data, format="csv", stats=self._stats
        )
