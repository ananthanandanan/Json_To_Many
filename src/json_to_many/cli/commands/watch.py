from __future__ import annotations

import glob
import os
import time
from datetime import datetime
from typing import Any

import click

from ...main import convert
from .._helpers import parse_kv, split_csv

# Input formats convert() can read; a bare directory watch picks up all of them.
_INPUT_FORMATS = ("json", "csv", "jsonl")

_FORMAT_EXTENSIONS: dict[str, str] = {
    "markdown": "md",
    "xml": "xml",
    "csv": "csv",
    "html": "html",
    "jsonl": "jsonl",
    "sql": "sql",
    "json": "json",
}


def _build_options(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _output_path(output_dir: str, source: str, fmt: str) -> str:
    ext = _FORMAT_EXTENSIONS.get(fmt, fmt)
    stem = os.path.splitext(os.path.basename(source))[0]
    return os.path.join(output_dir, f"{stem}.{ext}")


def _discover(source: str, from_format: str | None) -> list[str]:
    """Resolve a file or directory into the concrete input paths to watch.

    A single file is watched as-is. A directory is scanned for files matching
    `from_format` (or every supported input extension when unspecified). The
    result is sorted so log output and tests are deterministic.
    """
    if os.path.isdir(source):
        extensions = (from_format,) if from_format else _INPUT_FORMATS
        paths: list[str] = []
        for ext in extensions:
            paths.extend(glob.glob(os.path.join(source, f"*.{ext}")))
        return sorted(set(paths))
    return [source]


def _run_once(
    source: str,
    mtimes: dict[str, float],
    formats: tuple[str, ...],
    output_dir: str,
    from_format: str | None,
    options: dict[str, Any],
    log,
) -> int:
    """Perform one scan pass: convert any file whose mtime changed.

    `mtimes` is mutated in place so the caller carries state between passes.
    Returns the number of (file × format) outputs rebuilt this pass. Conversion
    errors are logged and swallowed so a bad save never kills the loop.
    """
    rebuilt = 0
    for path in _discover(source, from_format):
        try:
            mtime = os.stat(path).st_mtime
        except FileNotFoundError:
            # File vanished between discovery and stat; retry next pass.
            continue
        if mtimes.get(path) == mtime:
            continue
        mtimes[path] = mtime
        for fmt in formats:
            out_path = _output_path(output_dir, path, fmt)
            stamp = datetime.now().strftime("%H:%M:%S")
            try:
                convert(
                    path,
                    fmt,
                    output_file=out_path,
                    from_format=from_format,
                    **options,
                )
            except Exception as exc:  # noqa: BLE001 — keep watching after a bad file
                log(f"[{stamp}] {path} → {fmt}: ERROR {exc}")
                continue
            log(f"[{stamp}] {path} → {out_path}")
            rebuilt += 1
    return rebuilt


@click.command("watch")
@click.argument("source")
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
    help="Explicit input format. When SOURCE is a directory, also filters "
    "which files are watched. Auto-detected from extension otherwise.",
)
@click.option(
    "--output-dir",
    "-d",
    required=True,
    help="Output directory. Files are auto-named by input stem.",
)
@click.option(
    "--interval",
    type=float,
    default=0.25,
    show_default=True,
    help="Polling interval in seconds (os.stat mtime polling, no watchdog dep).",
)
@click.option("--quiet", is_flag=True, help="Suppress the rebuild log.")
# Markdown / template options
@click.option(
    "--template",
    default=None,
    type=click.Choice(["openapi"], case_sensitive=False),
    help="Render Markdown with a structure-aware template (e.g. 'openapi').",
)
@click.option("--title", default=None, help="Markdown document title.")
@click.option(
    "--heading-offset", type=int, default=None, help="Heading level offset (Markdown)."
)
@click.option(
    "--frontmatter",
    multiple=True,
    callback=parse_kv,
    help="YAML frontmatter as key=val (repeatable, string values only).",
)
# CSV / SQL pass-through
@click.option("--delimiter", default=None, help="CSV field delimiter (default: ',').")
@click.option(
    "--columns",
    default=None,
    callback=split_csv,
    help="Comma-separated fields to emit (CSV/SQL). Nested keys use dot notation.",
)
@click.option("--table", default=None, help="Table name for SQL output.")
@click.option(
    "--include-create",
    "include_create",
    is_flag=True,
    default=None,
    help="Emit a CREATE TABLE statement before INSERTs (SQL).",
)
def watch_cmd(
    source: str,
    formats: tuple[str, ...],
    from_format: str | None,
    output_dir: str,
    interval: float,
    quiet: bool,
    template: str | None,
    title: str | None,
    heading_offset: int | None,
    frontmatter: dict[str, str] | None,
    delimiter: str | None,
    columns: list[str] | None,
    table: str | None,
    include_create: bool | None,
) -> None:
    """Watch a file or directory and re-render on every change.

    SOURCE is a file or directory. Each changed input is converted into
    --output-dir, auto-named by its stem. Polls os.stat() mtimes — no extra
    dependencies. Press Ctrl+C to stop.

    \b
    Examples:
      json2many watch api/ --to markdown --template openapi --output-dir docs/api/
      json2many watch data.json --to csv --to html --output-dir dist/
    """
    if not os.path.exists(source):
        raise click.ClickException(f"No such file or directory: {source}")

    paths = _discover(source, from_format)
    if not paths:
        raise click.ClickException(f"No input files found to watch in {source!r}")

    os.makedirs(output_dir, exist_ok=True)

    options = _build_options(
        template=template,
        title=title,
        heading_offset=heading_offset,
        frontmatter=frontmatter,
        delimiter=delimiter,
        columns=columns,
        table=table,
        include_create=include_create,
    )

    def log(message: str) -> None:
        if not quiet:
            click.echo(message, err=True)

    click.echo(
        f"Watching {len(paths)} file(s). Press Ctrl+C to stop.",
        err=True,
    )

    # Build everything once up front so outputs exist before the first edit.
    mtimes: dict[str, float] = {}
    _run_once(source, mtimes, formats, output_dir, from_format, options, log)

    try:
        while True:
            time.sleep(interval)
            _run_once(source, mtimes, formats, output_dir, from_format, options, log)
    except KeyboardInterrupt:
        click.echo("\nStopped.", err=True)
