# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

```bash
# Install runtime + CLI extra + dev tooling
uv sync --extra cli --dev

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_converters/test_csv_converter.py -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Build distribution
uv build

# Release (patch | minor | major)
./scripts/release.sh patch
```

## Architecture

### Public API (`src/json_to_many/__init__.py`)

Two top-level functions are exported:

- **`convert(json_input, output_format, output_file=None, **options) → ConversionResult`** — accepts a file path, JSON string, or Python dict/list; dispatches to the appropriate converter; applies `.json2many.toml` config before forwarding options.
- **`analyze_schema(data) → SchemaResult`** — inspects field names, types, coverage percentages, and samples without converting.

Also exported: `ConversionResult`, `ConversionStats`, `SchemaResult`, `FieldInfo`, `JsonToManyError`, `UnsupportedFormatError`.

### Converter Pattern

`src/json_to_many/converters/base_converter.py` — `BaseConverter` (ABC) with three abstract methods: `converter()`, `save_to_file()`, `get_converted_data()`. Each subclass receives `self.data` and `self.options` (the merged kwargs dict).

All six converters follow the same lifecycle: instantiate with `(data, **options)` → call `.converter()` → call `.get_converted_data()` → optionally `.save_to_file(path)`. The `save_to_file` methods all read `self.options.get("encoding", DEFAULT_ENCODING)` — do not hardcode the encoding constant.

Format-specific notes:
- **`csv_converter.py`** — uses `flatten_json()` for nested keys; honours `delimiter`, `quotechar`, `include_header`, `columns`.
- **`sql_converter.py`** — calls `analyze_schema()` internally when `include_create=True` to infer `INTEGER`/`REAL`/`TEXT` column types; `bool` must be checked before `int` in type inference (Python subclass trap).
- **`html_converter.py`** — all values are escaped via `html.escape()`; `table_style="bootstrap"` injects a CDN link.
- **`markdown_converter.py`** — recursive descent; `table_for_lists=True` renders list-of-dicts as a Markdown table.

### Config System (`src/json_to_many/config.py`)

`load_config()` walks up the directory tree from `cwd` looking for `.json2many.toml` (same strategy as `git` / `.gitignore`). Returns `{}` if not found or if `tomllib` is unavailable.

`merge_options(config, output_format, explicit_options)` applies a three-layer priority:

```
explicit_options  >  [converters.<format>]  >  [defaults]
```

This merge happens inside `convert()` in `main.py` before the converter is instantiated.

`tomllib` is stdlib on Python ≥ 3.11; on 3.10 it falls back to the `tomli` package (listed in `dependencies` with a version marker).

### Schema Engine (`src/json_to_many/utils/schema.py`)

`analyze_schema()` flattens each record with `flatten_json()`, accumulates per-field value counts and type sets, strips `"null"` from the type set before resolving to `"mixed"` or the single type, and sorts results by coverage descending then alphabetically. Used by both the library API and `SqlConverter` (for `CREATE TABLE` type inference).

### CLI (`src/json_to_many/cli/`)

Entry point: `json_to_many.cli.main:cli` (registered as `json2many` script). Click is an optional dependency (`pip install 'json_to_many[cli]'`); the module guards against a missing import with a graceful error.

- **`commands/convert.py`** — `--to` is repeatable; `--output` is single-format only; `--output-dir` auto-names files by stem; `--dry-run` writes to stdout; stats are written to **stderr** so stdout stays pipe-clean; `--json` emits the full `ConversionResult` as JSON.
- **`commands/schema.py`** — `--json` emits `SchemaResult` as JSON; `--top N` slices by coverage; plain-text table uses `str.ljust()` with Unicode `─` dividers.

### Adding a New Format

1. Create `src/json_to_many/converters/<name>_converter.py` subclassing `BaseConverter`.
2. Register it in the `_CONVERTERS` dict in `src/json_to_many/main.py`.
3. Add the format name to `SUPPORTED_FORMATS` in `src/json_to_many/utils/constants.py`.
4. Expose any format-specific CLI flags in `src/json_to_many/cli/commands/convert.py`.

## Release Process

Releases use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). `git-cliff` (`cliff.toml`) auto-generates `CHANGELOG.md`. See `RELEASING.md` for the full workflow.
