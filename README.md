# Json_To_Many

[![PyPI Version](https://img.shields.io/pypi/v/json_to_many.svg)](https://pypi.org/project/json_to_many/)
[![License](https://img.shields.io/pypi/l/json_to_many.svg)](https://github.com/ananthanandanan/Json_To_Many/blob/main/LICENSE)
[![Build Status](https://github.com/ananthanandanan/Json_To_Many/actions/workflows/ci.yml/badge.svg)](https://github.com/ananthanandanan/Json_To_Many/actions)

## Overview

**Json_To_Many** is a zero-dependency Python library for converting JSON data into multiple output formats — Markdown, XML, CSV, and more. It is built for developers who need format conversion as part of a codebase, script, or CI pipeline — not as a one-off manual task.

Every conversion returns a typed `ConversionResult` so callers never need to parse raw output strings. The package ships `py.typed` and full annotations, so mypy and pyright work without any extra configuration.

### What developers use it for

- Generating Markdown documentation from API responses or config data
- Producing XML output for legacy system integration
- Exporting structured data as CSV for downstream tooling
- Automating format conversion in CI pipelines

### Design principles

- **Zero mandatory dependencies** — `pip install json_to_many` brings nothing else with it
- **Typed by default** — full annotations, `py.typed` marker, works with strict mypy/pyright
- **Structured return type** — `ConversionResult.data`, `.format`, `.stats` — no string parsing
- **Composable** — plays cleanly with `jq`, shell pipes, and GitHub Actions

## Features

### Output Formats

| Format   | Options |
|----------|---------|
| Markdown | `title`, `heading_offset`, `max_heading_level`, `bullet_lists`, `table_for_lists`, `frontmatter`, `code_block_keys` |
| XML      | `root_element`, `item_element`, `pretty_print` |
| CSV      | `delimiter`, `quotechar`, `include_header`, `columns` |


## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Converting JSON to Markdown](#converting-json-to-markdown)
    - [Markdown Options](#markdown-options)
  - [Converting JSON to XML](#converting-json-to-xml)
    - [XML Options](#xml-options)
  - [Converting JSON to CSV](#converting-json-to-csv)
    - [CSV Options](#csv-options)
- [Examples](#examples)
- [Development](#development)
  - [Setting Up a Development Environment](#setting-up-a-development-environment)
  - [Coding Guidelines](#coding-guidelines)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

Install **Json_To_Many** using `pip`:

```bash
pip install json_to_many
```

Or, if you prefer using uv:

```bash
uv add json_to_many
```

## Quick Start

```python
from json_to_many import convert

# Convert JSON string to Markdown and save to 'output.md'
json_string = '{"title": "Sample Document", "content": "This is a sample."}'
convert(json_string, 'markdown', output_file='output.md')

# Convert JSON file to XML — always returns a ConversionResult
result = convert('data.json', 'xml')
print(result.data)   # the XML string
print(result.stats)  # ConversionStats(rows=..., fields=...)
```

## Usage

### Converting JSON to Markdown

**From a JSON File:**

```python
from json_to_many import convert

# Convert JSON file to Markdown and save to 'output.md'
convert('data.json', 'markdown', output_file='output.md')
```

**From a JSON String:**

```python
from json_to_many import convert

json_string = '{"title": "Sample Document", "content": "This is a sample."}'

result = convert(json_string, 'markdown')
print(result.data)
```

**Sample Output:**

```markdown
# title

Sample Document

# content

This is a sample.
```

### Markdown Options

The Markdown converter accepts optional keyword arguments to customise its output. All options are passed directly to `convert()`.

#### Layout options

| Option | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | `None` | Prepends `# {title}` at the top of the document |
| `heading_offset` | `int` | `0` | Shifts all heading levels by this amount (e.g. `1` makes top-level keys H2) |
| `max_heading_level` | `int` | `6` | Keys deeper than this render as `**bold**` instead of headings |
| `bullet_lists` | `bool` | `True` | Renders lists of primitives as `- item` bullet points |

**Example:**

```python
from json_to_many import convert

data = {
    "Project": {
        "Name": "MyApp",
        "Tech": ["Python", "FastAPI"],
    }
}

# Shift headings down one level and add a document title
result = convert(data, "markdown",
                 title="Project Report",
                 heading_offset=1,
                 bullet_lists=True)
print(result.data)
```

```markdown
# Project Report

## Project

### Name

MyApp

### Tech

- Python
- FastAPI
```

#### Tables

| Option | Type | Default | Description |
|---|---|---|---|
| `table_for_lists` | `bool` | `False` | Renders a list of dicts with common keys as a GFM pipe table |

**Example:**

```python
data = {
    "Users": [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob",   "role": "user"},
    ]
}

result = convert(data, "markdown", table_for_lists=True)
md = result.data
```

```markdown
# Users

| name | role |
| --- | --- |
| Alice | admin |
| Bob | user |
```

#### Frontmatter

| Option | Type | Default | Description |
|---|---|---|---|
| `frontmatter` | `dict` | `None` | Emits a YAML frontmatter block (for static site generators, Obsidian, etc.) |

Supports `str`, `int`, `float`, `bool`, and `None` values. No external dependencies required.

**Example:**

```python
result = convert(data, "markdown",
                 frontmatter={"title": "API Docs", "date": "2025-02-21", "draft": False})
md = result.data
```

```markdown
---
title: API Docs
date: 2025-02-21
draft: false
---

...content...
```

#### Code blocks

| Option | Type | Default | Description |
|---|---|---|---|
| `code_block_keys` | `list` | `[]` | Values for these keys are rendered as fenced code blocks |

**Example:**

```python
data = {
    "endpoint": "/users",
    "example_request": '{"filter": "active"}',
}

result = convert(data, "markdown", code_block_keys=["example_request"])
md = result.data
```

```markdown
# endpoint

/users

# example_request

\`\`\`example_request
{"filter": "active"}
\`\`\`
```

### Converting JSON to XML

**From a Python Dictionary:**

```python
from json_to_many import convert

json_data = {
    "note": {
        "to": "Alice",
        "from": "Bob",
        "message": "Hello, Alice!"
    }
}

# Convert JSON data to XML and save to 'note.xml'
convert(json_data, 'xml', output_file='note.xml')

# Get the converted data
result = convert(json_data, 'xml')
print(result.data)
```

**Sample Output:**

```xml
<root><note><to>Alice</to><from>Bob</from><message>Hello, Alice!</message></note></root>
```

### XML Options

| Option | Type | Default | Description |
|---|---|---|---|
| `root_element` | `str` | `"root"` | Name of the top-level XML element |
| `item_element` | `str \| None` | `None` | Wraps each list item in a named element (e.g. `"item"`) |
| `pretty_print` | `bool` | `False` | Indents the XML output for readability |

**Example:**

```python
data = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]

result = convert(data, "xml",
                 root_element="users",
                 item_element="user",
                 pretty_print=True)
print(result.data)
```

```xml
<users>
  <user>
    <id>1</id>
    <name>Alice</name>
  </user>
  <user>
    <id>2</id>
    <name>Bob</name>
  </user>
</users>
```

### Converting JSON to CSV

**From a Python List of Dictionaries:**

```python
from json_to_many import convert

json_data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Los Angeles"}
]

# Convert JSON data to CSV and save to 'data.csv'
convert(json_data, 'csv', output_file='data.csv')
```

**Get Converted CSV Data Without Saving:**

```python
result = convert(json_data, 'csv')
print(result.data)
```

**Sample Output:**

```csv
name,age,city
Alice,30,New York
Bob,25,Los Angeles
```

**Note:** The CSV converter automatically flattens nested JSON structures using dot-notation keys (e.g. `address.city`).

### CSV Options

| Option | Type | Default | Description |
|---|---|---|---|
| `delimiter` | `str` | `","` | Field separator character |
| `quotechar` | `str` | `'"'` | Character used to quote fields containing the delimiter |
| `include_header` | `bool` | `True` | Whether to include the header row |
| `columns` | `list[str] \| None` | `None` | Explicit column list; controls order and limits output to these fields |

**Example:**

```python
data = [
    {"name": "Alice", "role": "admin", "joined": "2024-01-01"},
    {"name": "Bob",   "role": "user",  "joined": "2024-03-15"},
]

# Semicolon-separated, specific columns only
result = convert(data, "csv",
                 delimiter=";",
                 columns=["name", "role"])
print(result.data)
```

```csv
name;role
Alice;admin
Bob;user
```

## Examples

The `examples` directory contains sample scripts and data to help you get started.

- **JSON to Markdown Conversion**: [json_to_markdown_example.py](examples/json_to_markdown_example.py)
- **JSON to XML Conversion**: [json_to_xml_example.py](examples/json_to_xml_example.py)
- **JSON to CSV Conversion**: [json_to_csv_example.py](examples/json_to_csv_example.py)

### Running Examples

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ananthanandanan/Json_To_Many.git
   cd Json_To_Many/examples
   ```

2. **Install Dependencies** (for development):

   ```bash
   uv sync
   ```

   Or install the package directly:

   ```bash
   pip install json_to_many
   ```

3. **Run an Example Script**:

   ```bash
   uv run python json_to_markdown_example.py
   # or if installed globally:
   python json_to_markdown_example.py
   ```

## Development

The project uses **uv** for dependency management and packaging, and **Ruff** for linting and code style enforcement.

### Setting Up a Development Environment

1. **Fork the Repository**:

   Click the "Fork" button at the top right corner of the repository page.

2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/ananthanandanan/Json_To_Many.git
   cd Json_To_Many
   ```

3. **Install Dependencies**:

   ```bash
   uv sync
   ```

4. **Run Tests**:

   ```bash
   uv run pytest
   ```

5. **Check Code Quality with Ruff**:

   ```bash
   uv run ruff check .
   ```

6. **Build the Package**:

   ```bash
   uv build
   ```

### Coding Guidelines

- **Code Style**: Follow PEP 8 guidelines. Use **Ruff** for linting and code style enforcement.
- **Testing**: Write unit tests for new features and bug fixes.
- **Documentation**: Update documentation and examples to reflect changes.

> **Maintainers:** See [RELEASING.md](RELEASING.md) for the full release process (version bump, tagging, GitHub Release, and PyPI publish).

## Contributing

Contributions are welcome! Here's how you can help:

- **Report Bugs**: If you find a bug, please report it by opening an issue.
- **Suggest Features**: Have an idea for a new feature? Feel free to share it.
- **Submit Pull Requests**: If you'd like to fix a bug or implement a feature, you're welcome to contribute code.

### Guidelines for Contributing

1. **Create an Issue**:

   Before starting work on a feature or bug fix, please create an issue to discuss it.

2. **Branch Naming**:

   Use descriptive branch names, e.g., `feature/json-to-yaml` or `bugfix/fix-xml-output`.

3. **Pull Requests**:
   - Include a clear description of the changes.
   - Reference the issue number.
   - Ensure all tests pass and code quality checks are successful.

4. **Code Quality**:
   - Run `uv run pytest` to ensure all tests pass.
   - Run `uv run ruff check .` to ensure code style compliance.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue or contact [K N Anantha nandanan](mailto:ananthanandanan@gmail.com).

---
