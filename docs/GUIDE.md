# Json2Many User Guide

> You have a JSON file. You need it in another format. This guide shows you how — from a quick
> inspection in the terminal to a polished HTML report, a SQL seed file, or a locked-in team
> config that makes flags disappear.

---

## 1. You receive a JSON file you've never seen before

A colleague drops `api_export.json` on you. Before you convert anything, you want to know what's
actually in it — how many records, which fields exist, whether any are sparse.

```bash
json2many schema api_export.json
```

```
1247 records · 11 fields

Field             Type    Coverage   Sample
──────────────────────────────────────────────────────────────
id                int     100.0%     1
name              str     100.0%     "Alice Nguyen"
email             str     97.6%      "alice@example.com"
created_at        str     100.0%     "2024-01-15T09:23:11Z"
address.city      str     84.3%      "London"
address.country   str     84.3%      "GB"
score             float   61.2%      8.4
tags              str     55.1%      "admin, user"
notes             str     22.4%      "Onboarded via SSO"
deleted_at        null    8.1%       null
internal_id       str     3.2%       "ORG-00142"
```

One second. You now know: 1,247 records, `email` has gaps (97.6%), `score` is sparse (61.2%),
`deleted_at` is almost always null, and `address` is a nested object that gets flattened with
dot-notation.

**Narrow the view** when you only care about the most populated fields:

```bash
json2many schema api_export.json --top 5
```

**Pipe it into `jq`** to find every field below 100% coverage:

```bash
json2many schema api_export.json --json \
  | jq '.fields[] | select(.coverage < 100) | {name, coverage}'
```

```json
{"name": "email", "coverage": 97.6}
{"name": "address.city", "coverage": 84.3}
{"name": "score", "coverage": 61.2}
```

**From Python** — the same engine is available as a library function:

```python
from json_to_many import analyze_schema

result = analyze_schema("api_export.json")
print(result.record_count)   # 1247
for field in result.fields:
    if field.coverage < 100:
        print(f"{field.name}: {field.coverage}%")
```

---

## 2. Get the data as CSV — no script required

You want to load the data into a spreadsheet or hand it off to a data analyst. No Python,
no script:

```bash
json2many convert api_export.json --to csv --output report.csv
# Converted: api_export.json → report.csv (1247 rows, 11 fields)
```

**Preview before writing** — dry-run pipes the output to stdout without touching the filesystem:

```bash
json2many convert api_export.json --to csv --dry-run | head -5
```

**Pipe from stdin** — useful when the data comes from an API call:

```bash
curl -s https://api.example.com/users | json2many convert --to csv -
```

**From Python** — with full control over the output shape:

```python
from json_to_many import convert

result = convert("api_export.json", "csv",
    delimiter=";",           # European locale
    columns=["id", "name", "email"],  # select and order fields
    include_header=True,
)
print(result.data)           # the CSV string
print(result.stats.rows)     # 1247
```

The same controls are available on the CLI. `--columns` takes a comma-separated
list, matching how you'd type it at the prompt. Nested keys use dot notation
because CSV flattens automatically:

```bash
# Select and reorder fields
json2many convert api_export.json --to csv --columns id,name,email --output users.csv

# Address a nested field via dot notation
json2many convert api_export.json --to csv --columns id,address.city --output cities.csv

# Drop the header row when piping into a tool that doesn't want it
json2many convert api_export.json --to csv --no-header --output users.csv
```

**Preparing CSV for a Postgres `\COPY`** — typed columns choke on empty cells.
Use `--null-value` to emit a distinct sentinel and tell `psql` what it means:

```bash
json2many convert users.json --to csv --null-value '\N' --output users.csv
psql -c "\COPY users FROM 'users.csv' CSV HEADER NULL '\N'"
```

`--null-value` substitutes for both `null` values and missing keys; literal
empty-string values (`""`) are preserved as-is.

`delimiter='\t'` gives you TSV for free — no separate converter needed.

---

## 3. Multiple formats in one pass

You need the same data as CSV for the analyst, Markdown for the wiki, and HTML for the
manager — and you don't want to run the command three times:

```bash
json2many convert api_export.json \
  --to csv \
  --to markdown \
  --to html \
  --output-dir ./dist/
# Converted: api_export.json → dist/api_export.csv  (1247 rows, 11 fields)
# Converted: api_export.json → dist/api_export.md   (1247 rows)
# Converted: api_export.json → dist/api_export.html (1247 rows, 11 fields)
```

One pass, three files, same data.

---

## 4. Generating Markdown documentation

Your API returns a response you want to turn into readable docs. The Markdown converter
handles nested objects, lists, frontmatter, and tables — all from the same `convert()` call:

```python
from json_to_many import convert

result = convert("openapi_response.json", "markdown",
    title="API Users",
    heading_offset=1,        # start at H2 instead of H1
    max_heading_level=4,     # don't go deeper than H4
    table_for_lists=True,    # list-of-dicts → Markdown table
    frontmatter={"draft": False, "tags": ["api", "users"]},
)
```

Output (excerpt):

```markdown
---
draft: false
tags:
  - api
  - users
---

## API Users

| id | name  | email             |
|----|-------|-------------------|
| 1  | Alice | alice@example.com |
| 2  | Bob   | bob@example.com   |
```

**Render specific values as code blocks** — useful for API payloads or SQL snippets embedded
in your data:

```python
result = convert(data, "markdown",
    code_block_keys=["example_request", "sql_query"],
)
```

**Frontmatter from the CLI** — `--frontmatter key=val` is repeatable, useful in
CI where you want to stamp the generated doc with a date or git SHA:

```bash
json2many convert api.json --to markdown \
  --title "API reference" \
  --frontmatter draft=false \
  --frontmatter generated_at=2026-05-14 \
  --output docs/api.md
```

The first `=` splits the token, so values may contain `=`. Values are always
strings; if you need typed YAML values (numbers, booleans, lists), use the
Python API's `frontmatter=` argument instead.

---

## 5. XML for a legacy system

The receiving system expects XML. You control the element names and whether the output is
pretty-printed for readability or compact for transmission:

```python
result = convert("records.json", "xml",
    root_element="records",
    item_element="record",
    pretty_print=True,
)
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<records>
  <record>
    <id>1</id>
    <name>Alice</name>
  </record>
  <record>
    <id>2</id>
    <name>Bob</name>
  </record>
</records>
```

Without `pretty_print=True` you get a compact single-line output — smaller payload, same data.

---

## 6. An HTML report the manager can open in a browser

A manager asks for a formatted view of the data they can click through without installing
anything. Before this, you'd reach for Jinja or pandas. Now:

```bash
json2many convert api_export.json --to html --output report.html
```

Need it polished with Bootstrap?

```python
result = convert("api_export.json", "html",
    title="User Export — April 2026",
    table_style="bootstrap",
    wrap_in_page=True,
)
```

```html
<!DOCTYPE html>
<html>
<head>
  <title>User Export — April 2026</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5/...">
</head>
<body>
<table class="table table-striped">
  <thead><tr><th>id</th><th>name</th><th>email</th>...</tr></thead>
  <tbody>
    <tr><td>1</td><td>Alice Nguyen</td><td>alice@example.com</td></tr>
  </tbody>
</table>
</body>
</html>
```

All values are HTML-escaped — no XSS risk from data that contains `<`, `>`, or `"`.

`table_style` accepts three values:

| Value | Effect |
|---|---|
| `"none"` (default) | Plain `<table>` with no class |
| `"github"` | Adds `class="table"` |
| `"bootstrap"` | Adds `class="table table-striped"` and a Bootstrap CDN link |

A single dict (rather than a list) renders as a `<dl>` definition list instead of a table.

---

## 7. Feeding a log pipeline or fine-tuning a model

Your data needs to go into a system that expects JSON Lines: one object per line, no outer
array. Every log shipper, OpenAI fine-tuning upload, and Spark streaming job works this way.

```bash
json2many convert api_export.json --to jsonl --output users.jsonl
```

```jsonl
{"id": 1, "name": "Alice Nguyen", "email": "alice@example.com", "score": 8.4}
{"id": 2, "name": "Bob Smith", "email": null, "score": 7.1}
```

Non-ASCII characters — control them explicitly:

```python
convert(data, "jsonl", ensure_ascii=False)  # preserves ä, ü, ñ as-is
convert(data, "jsonl", ensure_ascii=True)   # escapes to \uXXXX (default)
```

---

## 8. Seeding a database from JSON fixture data

You have fixture data in JSON and need to load it into a database for integration testing.
Writing INSERT statements by hand is tedious and error-prone.

```bash
json2many convert users.json --to sql --output seed.sql
sqlite3 test.db < seed.sql
```

```sql
INSERT INTO data (id, name, email, score) VALUES
  (1, 'Alice Nguyen', 'alice@example.com', 8.4),
  (2, 'Bob Smith', NULL, 7.1),
  (3, 'O''Brien', 'obrien@example.com', 9.0);
```

`NULL` for missing values. `O''Brien` — single quotes doubled correctly. Booleans as `1`/`0`.

**Need the `CREATE TABLE` too?** Use `include_create` — types are inferred automatically
from the data using the same engine that powers `json2many schema`:

```python
result = convert("users.json", "sql",
    table="users",
    include_create=True,
    batch_size=500,
)
```

```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER,
  name TEXT,
  email TEXT,
  score REAL,
  active INTEGER,
  deleted_at TEXT
);

INSERT INTO users (id, name, email, score, active, deleted_at) VALUES
  (1, 'Alice Nguyen', 'alice@example.com', 8.4, 1, NULL),
  ...
```

`batch_size` splits large datasets into multiple INSERT statements — important for databases
with statement size limits. Default is 500 rows per batch.

**From the CLI** — every SQL knob worth tweaking per-invocation has a flag:

```bash
# Name the target table and emit a CREATE alongside the seed
json2many convert users.json --to sql \
  --table users \
  --include-create \
  --output seed.sql

# Narrow both INSERT and CREATE to a subset of fields
json2many convert users.json --to sql \
  --table users \
  --columns id,name,email \
  --include-create \
  --output seed.sql

# Substitute a token for NULL — useful when the consuming system distinguishes
# 'redacted' from 'unknown' from 'truly null'
json2many convert pii.json --to sql \
  --table users \
  --null-value redacted \
  --output seed.sql
```

`--null-value` always emits a quoted string literal in SQL, so passing
`--null-value NULL` produces `'NULL'` (the string), not the bare `NULL`
keyword. Omit the flag if you want the keyword.

---

## 9. Your team keeps running conversions differently

Every developer runs the same conversion with different flags. One uses `--delimiter ';'`,
another forgets it and gets commas, a third always forgets `--pretty-print` for XML. The
outputs are inconsistent and CI keeps breaking.

Add a `.json2many.toml` at the project root:

```toml
[defaults]
encoding = "utf-8"

[converters.csv]
delimiter = ";"
sort_columns = true
null_value = "N/A"

[converters.markdown]
heading_offset = 1
table_for_lists = true

[converters.xml]
pretty_print = true
root_element = "records"
item_element = "record"

[converters.sql]
table = "users"
include_create = true
batch_size = 500
```

Now every `json2many convert` in this directory picks up the config automatically — no flags
required. When a developer passes an explicit flag, it always wins over the config:

```bash
# Uses delimiter=";" from config
json2many convert data.json --to csv

# Overrides config: uses "|" instead
json2many convert data.json --to csv --delimiter '|'
```

The Python API respects the same config file — no extra wiring needed:

```python
from json_to_many import convert

# Picks up .json2many.toml from cwd — delimiter=";" applied automatically
result = convert("data.json", "csv")
```

The config file is found by walking up the directory tree from wherever you run the command,
the same way `git` finds `.gitignore`. Put it at the project root and it works from any
subdirectory.

**Priority order** (highest wins): explicit options > `[converters.<format>]` > `[defaults]`

---

## 10. Getting the result as structured JSON for scripting

Both `convert` and `schema` have a `--json` flag that emits the full result as JSON. This
makes every output scriptable with `jq` or any other tool:

```bash
# Check conversion stats in CI
json2many convert api_export.json --to csv --json | jq '.stats'
# {"rows": 1247, "fields": 11, "warnings": []}

# Find every field under 100% coverage
json2many schema api_export.json --json \
  | jq '.fields[] | select(.coverage < 100) | {name, coverage}'
```

The `--json` flag on `convert` emits the full `ConversionResult` structure. The `--json` flag
on `schema` emits the full `SchemaResult`. Both are stable — safe to rely on in scripts.
