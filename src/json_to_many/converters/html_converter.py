from __future__ import annotations

from html import escape
from typing import Any

from ..result import ConversionResult, ConversionStats
from ..utils.constants import DEFAULT_ENCODING
from .base_converter import BaseConverter

_BOOTSTRAP_CDN = (
    '<link rel="stylesheet" '
    'href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css">'
)


def _table_class(style: str) -> str:
    if style == "bootstrap":
        return ' class="table table-striped"'
    if style == "github":
        return ' class="table"'
    return ""


def _render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return _render_node(value)
    return escape(str(value))


def _render_node(data: Any, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(data, list):
        if data and all(isinstance(item, dict) for item in data):
            return _render_table(data, indent=indent)
        items = "\n".join(f"{pad}  <li>{_render_value(item)}</li>" for item in data)
        return f"{pad}<ul>\n{items}\n{pad}</ul>"
    if isinstance(data, dict):
        rows = ""
        for key, value in data.items():
            rendered = _render_value(value)
            rows += f"{pad}  <dt>{escape(str(key))}</dt>\n{pad}  <dd>{rendered}</dd>\n"
        return f"{pad}<dl>\n{rows}{pad}</dl>"
    return f"{pad}<p>{escape(str(data))}</p>"


def _render_table(records: list[dict], style: str = "none", indent: int = 0) -> str:
    pad = "  " * indent
    headers: list[str] = list(dict.fromkeys(k for row in records for k in row))
    cls = _table_class(style)

    head_cells = "".join(f"<th>{escape(h)}</th>" for h in headers)
    thead = f"{pad}  <thead><tr>{head_cells}</tr></thead>"

    body_rows = []
    for row in records:
        cells = "".join(f"<td>{_render_value(row.get(h))}</td>" for h in headers)
        body_rows.append(f"{pad}    <tr>{cells}</tr>")
    tbody = f"{pad}  <tbody>\n" + "\n".join(body_rows) + f"\n{pad}  </tbody>"

    return f"{pad}<table{cls}>\n{thead}\n{tbody}\n{pad}</table>"


class JsonToHTML(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.converted_data: str | None = None

    def converter(self) -> None:
        style: str = self.options.get("table_style", "none")
        wrap: bool = self.options.get("wrap_in_page", False)
        title: str = self.options.get("title", "")

        if isinstance(self.data, list) and self.data and all(isinstance(r, dict) for r in self.data):
            body = _render_table(self.data, style=style)
            rows = len(self.data)
            fields = len(dict.fromkeys(k for r in self.data for k in r))
        else:
            body = _render_node(self.data)
            rows = len(self.data) if isinstance(self.data, list) else 1
            fields = len(self.data) if isinstance(self.data, dict) else 0

        if wrap:
            cdn = f"\n  {_BOOTSTRAP_CDN}" if style == "bootstrap" else ""
            title_tag = f"\n  <title>{escape(title)}</title>" if title else ""
            self.converted_data = (
                f"<!DOCTYPE html>\n<html>\n<head>"
                f"{title_tag}{cdn}\n</head>\n<body>\n{body}\n</body>\n</html>"
            )
        else:
            self.converted_data = body

        self._stats = ConversionStats(rows=rows, fields=fields)

    def save_to_file(self, file_name: str) -> None:
        assert self.converted_data is not None
        with open(file_name, "w", encoding=DEFAULT_ENCODING) as f:
            f.write(self.converted_data)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(data=self.converted_data, format="html", stats=self._stats)
