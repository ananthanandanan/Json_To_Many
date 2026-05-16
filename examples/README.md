# Examples

This folder contains examples demonstrating how to use the `JsonToMany` package.

## JSON → other formats

- **`example.json`** — sample JSON input.
- **`json_to_markdown_example.py`** — JSON to Markdown.
- **`json_to_csv_example.py`** — JSON to CSV with nested flattening.
- **`json_to_xml_example.py`** — JSON to XML.
- **`conversion_result_demo.py`** — inspecting the `ConversionResult` dataclass.

## CSV → JSON (and other formats)

- **`users.csv`** — sample CSV with nested dotted columns, empty cells, and mixed types.
- **`csv_to_json_example.py`** — typed inference, `infer_types=False`, custom `null_values`,
  nested unflattening, and in-memory CSV strings via `from_format="csv"`.
- **`csv_to_markdown_example.py`** — the same CSV piped into Markdown, HTML, and SQL outputs.

## How to run

From the repo root:

```bash
uv run python examples/csv_to_json_example.py
uv run python examples/csv_to_markdown_example.py
uv run python examples/json_to_markdown_example.py
```
