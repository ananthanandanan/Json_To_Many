from __future__ import annotations

import dataclasses
import json
import sys

import click

from ...utils.json_utils import read_json_data
from ...utils.schema import SchemaResult, analyze_schema


def _render_table(result: SchemaResult, top: int | None) -> str:
    fields = result.fields[:top] if top else result.fields

    headers = ("Field", "Type", "Coverage", "Sample")
    rows = [(f.name, f.type, f"{f.coverage}%", f.sample) for f in fields]

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    sep = "  "
    header_line = sep.join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    divider = sep.join("─" * w for w in col_widths)
    data_lines = [
        sep.join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
        for row in rows
    ]

    plural = "record" if result.record_count == 1 else "records"
    field_count = len(fields)
    field_plural = "field" if field_count == 1 else "fields"
    summary = f"{result.record_count} {plural} · {field_count} {field_plural}"

    return "\n".join([summary, "", header_line, divider, *data_lines])


@click.command("schema")
@click.argument("source", default="-")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit SchemaResult as JSON (useful for scripting with jq).",
)
@click.option(
    "--top", type=int, default=None, help="Show only the top N fields by coverage."
)
def schema_cmd(source: str, as_json: bool, top: int | None) -> None:
    """Inspect the shape of a JSON file or stdin.

    SOURCE is a file path or - to read from stdin.

    \b
    Examples:
      json2many schema users.json
      json2many schema users.json --top 5
      json2many schema users.json --json | jq '.fields[] | select(.coverage < 100)'
      cat data.json | json2many schema
    """
    try:
        if source == "-":
            data = json.load(sys.stdin)
        else:
            data = read_json_data(source)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        raise click.ClickException(str(exc))

    result = analyze_schema(data)

    if as_json:
        click.echo(json.dumps(dataclasses.asdict(result), indent=2))
    else:
        click.echo(_render_table(result, top))
