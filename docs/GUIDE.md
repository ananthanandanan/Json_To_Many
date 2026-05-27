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

```bash
json2many convert records.json --to xml \
  --root-element records \
  --item-element record \
  --pretty-print \
  --output records.xml
```

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

`table_style` and `wrap_in_page` are Python-only — the CLI emits the plain default. Wrap the
call in a tiny script when you need a styled, standalone page.

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

## 9. Convert straight from Pydantic models, dataclasses, or ORM rows

You don't need to `.model_dump()` or `asdict()` before calling `convert`. Anything with a
`model_dump()`, `to_dict()`, or `@dataclass` decorator is normalized automatically — and the
check is duck-typed, so Pydantic isn't a hard dependency:

```python
from dataclasses import dataclass
from json_to_many import convert

@dataclass
class User:
    id: int
    name: str
    email: str

users = [User(1, "Alice", "alice@example.com"),
         User(2, "Bob",   "bob@example.com")]

result = convert(users, "csv")
```

The same call works with a list of Pydantic models (any version — `model_dump` is detected
duck-typed), SQLAlchemy rows that expose `to_dict()`, or any mix of plain dicts and objects.
Precedence: `model_dump` → dataclass → `to_dict`.

---

## 10. Pretty-printing or normalizing JSON

`--to json` is a first-class output format — useful for reformatting a minified payload,
sorting keys for diff-friendly output, or chaining into another step that wants JSON back:

```bash
# Minified API response → readable, sorted
json2many convert response.json --to json --indent 2 --sort-keys --output pretty.json

# Round-trip CSV through JSON, sorted
json2many convert users.csv --to json --sort-keys --indent 4 --output users.json
```

```python
from json_to_many import convert

result = convert(data, "json",
    indent=4,
    sort_keys=True,
    ensure_ascii=False,   # preserves é, ñ, 漢 — set True to escape to \uXXXX
)
```

`ensure_ascii` mirrors the stdlib `json` flag (CLI-only via the Python API — the CLI defaults
to keeping unicode as-is).

---

## 11. Your team keeps running conversions differently

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

## 12. You have a CSV and need it as JSON (or anything else)

A vendor exports a CSV. Your service consumes JSON. Or the QA team hands you a CSV and you
want a Markdown table for the bug report. Json2Many reads CSV through the same schema engine
that powers `schema`, so types come back typed — not everything-as-string.

```bash
json2many convert users.csv --to json --output users.json
# Converted: users.csv → users.json (5 rows, 6 fields)
```

The output is properly typed: `"42"` becomes `42`, `"true"` becomes `true`, `"8.4"` becomes
`8.4`. Empty cells (and `N/A`, `NULL`) become `null` by default.

```json
[
  {"id": 1, "name": "Alice Nguyen", "score": 8.4, "active": true, "address": {"city": "London"}},
  {"id": 2, "name": "Bob Smith",    "score": 7.1, "active": true, "address": {"city": "Berlin"}}
]
```

Dotted column names (`address.city`) unflatten back into nested objects automatically — so
`JSON → CSV → JSON` round-trips losslessly on nested data.

**Stdin needs an explicit `--from`** so the CLI doesn't have to guess:

```bash
curl -s https://reports.example.com/users.csv | json2many convert --from csv --to markdown
```

**Any output format works** — once CSV is parsed, the rest of the pipeline doesn't care
where the data came from:

```bash
json2many convert users.csv --to markdown --output users.md
json2many convert users.csv --to sql --table users --include-create --output seed.sql
json2many convert users.csv --to html --output report.html
```

**From Python** — pass a path, a `Path`, an in-memory string, or any file-like object:

```python
from json_to_many import convert

# File path — extension picks the reader
result = convert("users.csv", "json", indent=2)

# In-memory CSV string — be explicit
csv_text = "id,name,active\n1,Alice,true\n2,Bob,false\n"
result = convert(csv_text, "json", from_format="csv")

# Opt out of type inference — every value stays a string
result = convert("users.csv", "json", infer_types=False)

# Custom null tokens
result = convert("users.csv", "json", null_values=["", "unknown", "-"])

# Headerless CSV — columns auto-named col_0, col_1, ...
result = convert("rows.csv", "json", header=False)

# Any file-like object also works — handy for in-process pipelines
import io
buf = io.StringIO("id,name\n1,Alice\n")
result = convert(buf, "json", from_format="csv")
```

**CLI flags for reader options:**

| Flag | Effect |
|---|---|
| `--from {csv,json}` | Force the input format (required for stdin CSV). |
| `--infer-types / --no-infer-types` | Toggle per-cell type inference. Default on. |
| `--null-values empty,N/A,NULL` | Comma-separated tokens that become `null`. |
| `--no-header` | Treat the first row as data, auto-name columns `col_0`, `col_1`, … |
| `--delimiter ';'` | CSV field delimiter (applies to both reading and writing). |
| `--quotechar "'"` | CSV quote character. |
| `--flatten-sep '_'` | Separator used by the unflatten step (default `.`). |

**Type inference rules** (per-cell, in order):

1. Cell text matches one of `null_values` → `null`.
2. Parses as `int` → `int` (note: this runs before float, so `"42"` stays an int, not `42.0`).
3. Parses as `float` → `float`.
4. Case-insensitive `true` / `false` → `bool`. Strict — `1`/`0` stay int, `yes`/`no` stay str.
5. Anything else → `str`.

When `infer_types=False`, only step 1 still applies; everything else stays a string.

---

## 13. Getting the result as structured JSON for scripting

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

---

## 14. Catching errors cleanly

The library raises a small typed hierarchy so callers can catch *only* what they expect
without swallowing unrelated exceptions:

```python
from json_to_many import convert, JsonToManyError, UnsupportedFormatError

try:
    result = convert("data.json", "yaml")   # not a supported format
except UnsupportedFormatError as exc:
    print(f"Pick a different format: {exc}")
except JsonToManyError as exc:
    print(f"Conversion failed: {exc}")
```

- `JsonToManyError` — base class for everything the library raises. Catch this if you want
  one umbrella.
- `UnsupportedFormatError` — subclass of `JsonToManyError`, raised for unknown `output_format`
  or `from_format` values.

Standard library exceptions (`FileNotFoundError`, `json.JSONDecodeError`, `csv.Error`, etc.)
propagate as-is — they're not wrapped. That keeps stack traces honest when the failure is
upstream of the converter.

---

## 15. Turning an OpenAPI spec into readable API docs

An OpenAPI spec is precise but unreadable — nobody opens `openapi.json` to *understand* an
API. This template turns it into plain Markdown that drops straight into the places people
actually read and search:

- **GitHub / GitLab** — commit `API.md` and it renders as a browsable reference right next to
  the code, diffing in PRs as the API changes.
- **Notion, Obsidian, Confluence** — paste or import the Markdown; tables, headings, and
  anchor links all survive, so the reference lives in your team's wiki without a doc pipeline.
- **Static docs sites** — feed it to MkDocs, Docusaurus, or mdBook, which take Markdown natively.
- **LLM / RAG context** — Markdown is the friendliest format for putting an API into a model's
  context window or a vector store. A flat, linked `API.md` is far better grounding for "write
  a client for this endpoint" than raw spec JSON.

```bash
json2many convert openapi.json --to markdown --template openapi --output API.md
```

**You almost certainly already have the spec — don't write it by hand.** Most backend
frameworks emit it for you: FastAPI serves it at `/openapi.json`, Spring via `springdoc`,
NestJS via `@nestjs/swagger`, .NET via Swashbuckle, Django via `drf-spectacular`. If your app
is running, skip the file on disk and pipe the live endpoint straight in:

```bash
curl localhost:8000/openapi.json | json2many convert - --to markdown --template openapi --output API.md
```

The `--template openapi` flag switches the Markdown converter from generic key/value descent
into an OpenAPI-aware renderer. The output covers, in order:

- an **info block** — title, version, description, and servers;
- an **Authentication** section built from `components.securitySchemes` (API keys, bearer/JWT,
  OAuth2 flows), with a per-endpoint `Security:` note;
- **endpoints grouped by tag** — each operation under its first tag, untagged ones collected
  under an `Other` section at the end;
- **parameters, request bodies, and responses** as GitHub-flavored tables, with status codes;
- a trailing **Schemas** section — every `$ref` renders as a link (e.g. `[Pet](#pet)`) into a
  property table rendered once, so shared and even circular schemas stay DRY and terminate.

Examples are emitted as fenced ` ```json ` blocks, and every table cell is escaped so a stray
`|` in a description never breaks the layout.

Preview before writing a file with `--dry-run`, or call it from Python:

```python
from json_to_many import convert

convert("openapi.json", "markdown", template="openapi", output_file="API.md")
```

Supported spec versions are **OpenAPI 3.0 and 3.1**. A Swagger 2.0 spec, or any JSON that
isn't an OpenAPI document, raises `JsonToManyError` with a message explaining what was
expected — so a wrong file in a CI step fails loudly rather than producing nonsense.

## 16. Live-reload: keep output in sync while you edit (`watch`)

`json2many watch` is `convert` on a loop — the `tsc --watch` / `sass --watch` ergonomic
applied to "source file in, formatted output out." When you're iterating on a file and want
to *see the rendered result* without re-running the command, point `watch` at it and leave it
running.

**The everyday case — a live-previewed report from a data file.** You're tweaking a JSON file
(a team roster, a config dump, exported query results) and want an HTML view that stays
current:

```bash
json2many watch . --from json --to html --output-dir out/
# Watching 1 file(s). Press Ctrl+C to stop.
# [14:20:03] ./team.json → out/team.html
```

Open `out/team.html` in a browser tab. Now the loop is: edit `team.json` → save → `watch`
regenerates the HTML → refresh the tab. You iterate on the *data* and see the *rendered
report*, never touching the command again. Swap `--to html` for `--to markdown` and preview
in your editor (VS Code: `Cmd+Shift+V`) instead.

**Regenerating SQL seed data from fixtures.** Editing JSON fixtures for integration tests and
want a fresh seed file each save:

```bash
json2many watch fixtures/ --to sql --table users --include-create --output-dir build/
```

Edit a fixture, and `build/<name>.sql` rebuilds with updated `CREATE` + `INSERT`s, ready to
pipe into your test DB.

### How it works

`SOURCE` may be a file or a directory. A directory is scanned for every supported input
extension (`json`, `csv`, `jsonl`); pass `--from json` to narrow that. Each changed input is
converted into `--output-dir`, auto-named by its stem — the same naming `convert --output-dir`
uses. New files dropped into a watched directory are picked up on the next scan, and a file
that fails to convert logs an error and is retried on its next change rather than killing the
loop.

Detection is plain `os.stat()` mtime polling (default every 250 ms, tune with `--interval`) —
no `watchdog` dependency, keeping the base install dependency-free. Every `convert` flag for
the chosen format applies (`--columns`, `--table`, `--template`, …), so anything `convert`
can produce, `watch` can keep live. Press `Ctrl+C` to stop.

> **`watch` watches files on disk, not URLs.** It can't poll an HTTP endpoint — so the
> `curl localhost:8000/openapi.json | convert -` pattern from §15 doesn't combine with
> `watch`. Use `watch` when you're editing a spec or data file that lives in your repo; use the
> `curl` one-liner (or a git hook / CI step) for a spec your framework serves over HTTP.

### Editing an OpenAPI spec? Same loop, add `--template openapi`

If you maintain `openapi.json` by hand (design-first), `watch` gives you live API docs as you
edit — split-screen the spec and the rendered `docs/openapi.md` preview:

```bash
json2many watch . --from json --to markdown --template openapi --output-dir docs/
# [14:02:11] ./openapi.json → docs/openapi.md
```
