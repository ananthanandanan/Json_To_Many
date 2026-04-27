# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Json2Many** is a zero-dependency Python library that converts JSON data into multiple output formats (Markdown, XML, CSV). Managed with `uv` and built with Hatchling, using a `src/` layout.

## Common Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_converters/test_markdown_converter.py -v

# Lint and format
uv run ruff check .
uv run ruff format .

# Build distribution
uv build

# Release (patch | minor | major)
./scripts/release.sh patch
```

## Architecture

### Entry Point

`src/json_to_many/main.py` — `convert()` is the single public entry point. It accepts a file path, JSON string, or Python dict/list, then routes to the appropriate converter based on `output_format`. All extra `**options` are forwarded to the converter.

### Converter Pattern

`src/json_to_many/converters/base_converter.py` defines `BaseConverter` (ABC) with three abstract methods: `converter()`, `save_to_file()`, and `get_converted_data()`. Each format subclass receives `self.data` and `self.options` (the forwarded kwargs).

- **`markdown_converter.py`** — Recursive descent parser; supports `title`, `heading_offset`, `max_heading_level`, `bullet_lists`, `table_for_lists`, `frontmatter`, `code_block_keys`.
- **`xml_converter.py`** — Uses stdlib `xml.etree.ElementTree`; recursive element creation.
- **`csv_converter.py`** — Uses `flatten_json()` from utils to flatten nested JSON, then `csv.DictWriter`.

### Utils

- `json_utils.py` — `read_json_data()` handles all input types; `flatten_json()` flattens nested dicts with dot-notation keys (lists become comma-separated strings).
- `validation.py` — `validate_json()` checks input is dict or list.
- `constants.py` — `DEFAULT_ENCODING`, `SUPPORTED_FORMATS`.
- `exceptions.py` — `JsonToManyError` (base), `UnsupportedFormatError`, `ConversionError`.

### Public API

`src/json_to_many/__init__.py` exports only `convert` and the exception classes. Adding a new format means: create a converter subclass, register it in `main.py`'s dispatch, and add to `SUPPORTED_FORMATS`.

## Roadmap Context

Development follows a phased plan tracked in `.cursor/plans/`. Chunks 1.1–1.3 (options passthrough, Markdown options) are complete. Chunks 1.4–1.6 (XML/CSV options, `ConversionResult` dataclass) are next. Phases 2–4 cover CLI, new formats, templates/plugins, and AI features.

## Release Process

Releases use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`). `git-cliff` (`cliff.toml`) auto-generates `CHANGELOG.md`. See `RELEASING.md` for the full workflow.
