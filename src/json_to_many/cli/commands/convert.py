from __future__ import annotations

import dataclasses
import json
import os
import sys
from typing import Any

import click

from ...main import convert
from .._helpers import parse_kv, split_csv

_FORMAT_EXTENSIONS: dict[str, str] = {
    "markdown": "md",
    "xml": "xml",
    "csv": "csv",
    "html": "html",
    "jsonl": "jsonl",
    "sql": "sql",
    "json": "json",
}

_INPUT_FORMATS = ("json", "csv")


def _load_source(source: str, from_format: str | None) -> Any:
    """Return the value to hand to convert().

    For stdin, read text once and pass it as a string (convert() can re-parse
    based on `from_format`). For file paths, hand the path through and let
    convert() dispatch by extension or explicit override.
    """
    if source == "-":
        text = sys.stdin.read()
        if from_format == "csv":
            return text
        return json.loads(text)
    return source


def _build_options(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _output_path(output_dir: str, source: str, fmt: str) -> str:
    ext = _FORMAT_EXTENSIONS.get(fmt, fmt)
    stem = os.path.splitext(os.path.basename(source))[0] if source != "-" else "output"
    return os.path.join(output_dir, f"{stem}.{ext}")


@click.command("convert")
@click.argument("source", default="-")
@click.option(
    "--to",
    "-t",
    "formats",
    multiple=True,
    required=True,
    help="Output format (repeatable for multiple outputs).",
)
@click.option(
    "--from",
    "-f",
    "from_format",
    type=click.Choice(_INPUT_FORMATS, case_sensitive=False),
    default=None,
    help="Explicit input format. Required for stdin CSV; "
    "auto-detected from file extension otherwise.",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    default=None,
    help="Output file path. Only valid with a single --to.",
)
@click.option(
    "--output-dir",
    "-d",
    default=None,
    help="Output directory for multiple --to formats.",
)
@click.option("--dry-run", is_flag=True, help="Print output without writing any files.")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit ConversionResult as JSON (useful for scripting).",
)
@click.option("--quiet", is_flag=True, help="Suppress stats output.")
# CSV options (shared between reader and writer where applicable)
@click.option("--delimiter", default=None, help="CSV field delimiter (default: ',').")
@click.option("--quotechar", default=None, help="CSV quote character (default: '\"').")
@click.option(
    "--columns",
    default=None,
    callback=split_csv,
    help="Comma-separated list of fields to emit (e.g. id,name,email). "
    "Also applies to SQL. Nested keys use dot notation.",
)
@click.option(
    "--header/--no-header",
    "header",
    default=None,
    help="CSV header behaviour. When reading: first row is column names "
    "(default). When writing: emit a header row (default).",
)
@click.option(
    "--null-value",
    default=None,
    help="Token to emit for null or missing values (CSV cell or SQL string "
    "literal). Note: passing 'NULL' produces the quoted literal \"'NULL'\" in "
    "SQL, not the bare NULL keyword.",
)
@click.option(
    "--null-values",
    default=None,
    callback=split_csv,
    help="Comma-separated tokens to interpret as null when reading CSV "
    "(default: empty,N/A,NULL).",
)
@click.option(
    "--infer-types/--no-infer-types",
    "infer_types",
    default=None,
    help="Type inference when reading CSV. Default: --infer-types.",
)
@click.option(
    "--flatten-sep",
    default=None,
    help="Separator for flattened nested keys (CSV/SQL). Default: '.'. "
    "Useful when dots clash with downstream tools (e.g. '_' for SQL columns).",
)
# JSON output options
@click.option(
    "--indent",
    type=int,
    default=None,
    help="JSON output indent (default: 2).",
)
@click.option(
    "--sort-keys",
    is_flag=True,
    default=None,
    help="Sort object keys in JSON output.",
)
# XML options
@click.option("--root-element", default=None, help="XML root element name.")
@click.option("--item-element", default=None, help="XML item element name.")
@click.option(
    "--pretty-print", is_flag=True, default=False, help="Pretty-print XML output."
)
# Markdown options
@click.option("--title", default=None, help="Markdown document title.")
@click.option(
    "--heading-offset",
    type=int,
    default=None,
    help="Heading level offset for Markdown output.",
)
@click.option(
    "--frontmatter",
    "frontmatter",
    multiple=True,
    callback=parse_kv,
    help="YAML frontmatter as key=val (repeatable, string values only).",
)
# SQL options
@click.option(
    "--table", default=None, help="Table name for SQL INSERT / CREATE statements."
)
@click.option(
    "--include-create",
    "include_create",
    is_flag=True,
    default=None,
    help="Emit a CREATE TABLE statement before INSERTs (SQL).",
)
def convert_cmd(
    source: str,
    formats: tuple[str, ...],
    from_format: str | None,
    output_file: str | None,
    output_dir: str | None,
    dry_run: bool,
    as_json: bool,
    quiet: bool,
    delimiter: str | None,
    quotechar: str | None,
    columns: list[str] | None,
    header: bool | None,
    null_value: str | None,
    null_values: list[str] | None,
    infer_types: bool | None,
    flatten_sep: str | None,
    indent: int | None,
    sort_keys: bool | None,
    root_element: str | None,
    item_element: str | None,
    pretty_print: bool,
    title: str | None,
    heading_offset: int | None,
    frontmatter: dict[str, str] | None,
    table: str | None,
    include_create: bool | None,
) -> None:
    """Convert a JSON or CSV file (or stdin) to one or more output formats.

    SOURCE is a file path or - to read from stdin.

    \b
    Examples:
      json2many convert data.json --to markdown --output report.md
      cat data.json | json2many convert --to csv
      json2many convert data.json --to markdown --to csv --output-dir ./dist/
      json2many convert data.csv --to json --output users.json
      cat data.csv | json2many convert --from csv --to markdown
      json2many convert data.json --to xml --dry-run
      json2many convert data.json --to csv --columns id,name,email
      json2many convert data.json --to sql --table users --include-create
    """
    if output_file and len(formats) > 1:
        raise click.UsageError("--output can only be used with a single --to format.")
    if output_file and output_dir:
        raise click.UsageError("--output and --output-dir are mutually exclusive.")

    try:
        data = _load_source(source, from_format)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        raise click.ClickException(str(exc))

    # `header` covers both the CSV reader (`header=`) and writer (`include_header=`).
    include_header = header

    converter_opts = _build_options(
        delimiter=delimiter,
        quotechar=quotechar,
        columns=columns,
        header=header,
        include_header=include_header,
        null_value=null_value,
        null_values=null_values,
        infer_types=infer_types,
        flatten_sep=flatten_sep,
        indent=indent,
        sort_keys=sort_keys,
        root_element=root_element,
        item_element=item_element,
        pretty_print=pretty_print if pretty_print else None,
        title=title,
        heading_offset=heading_offset,
        frontmatter=frontmatter,
        table=table,
        include_create=include_create,
    )

    results = {}
    for fmt in formats:
        out_path: str | None = None
        if not dry_run:
            if output_file:
                out_path = output_file
            elif output_dir:
                os.makedirs(output_dir, exist_ok=True)
                out_path = _output_path(output_dir, source, fmt)

        try:
            result = convert(
                data,
                fmt,
                output_file=out_path,
                from_format=from_format,
                **converter_opts,
            )
        except Exception as exc:
            raise click.ClickException(f"[{fmt}] {exc}")

        results[fmt] = result

        if dry_run:
            click.echo(f"--- {fmt} (dry run) ---")
            click.echo(result.data)
        elif as_json:
            click.echo(json.dumps(dataclasses.asdict(result), indent=2))
        elif not quiet:
            dest = out_path or "stdout"
            rows_info = f"{result.stats.rows} rows" if result.stats.rows else ""
            fields_info = f"{result.stats.fields} fields" if result.stats.fields else ""
            stats = ", ".join(filter(None, [rows_info, fields_info]))
            msg = f"Converted: {source} → {dest}"
            if stats:
                msg += f" ({stats})"
            click.echo(msg, err=True)

        if not dry_run and not as_json and out_path is None:
            click.echo(result.data)
