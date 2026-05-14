from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from json_to_many.cli.main import cli


USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "score": 9},
    {"id": 2, "name": "Bob", "email": None},
    {"id": 3, "name": "Carol", "email": "carol@example.com", "score": 7},
]


def _write_input(tmp_path: Path) -> Path:
    src = tmp_path / "users.json"
    src.write_text(json.dumps(USERS))
    return src


# ── --columns ─────────────────────────────────────────────────────────────────


def test_columns_csv_narrows_output(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli, ["convert", str(src), "--to", "csv", "--columns", "id,name", "--dry-run"]
    )
    assert result.exit_code == 0, result.output
    assert "id,name" in result.output
    assert "email" not in result.output


def test_columns_sql_narrows_insert(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "sql",
            "--table",
            "users",
            "--columns",
            "id,name",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "INSERT INTO users (id, name) VALUES" in result.output
    assert "email" not in result.output


def test_columns_with_unknown_name_silent_blank_csv(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "csv",
            "--columns",
            "id,nonexistent",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    # Unknown column produces an empty cell, no error.
    assert "id,nonexistent" in result.output


def test_columns_plus_include_create_narrows_both(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "sql",
            "--table",
            "users",
            "--columns",
            "id,name",
            "--include-create",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    create_block = result.output.split(");")[0]
    assert "CREATE TABLE IF NOT EXISTS users" in create_block
    assert "id" in create_block
    assert "name" in create_block
    assert "email" not in create_block


# ── --null-value ──────────────────────────────────────────────────────────────


def test_null_value_csv_replaces_none_and_missing(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "csv",
            "--columns",
            "id,name,email,score",
            "--null-value",
            "\\N",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    lines = result.output.strip().splitlines()
    # Row for Bob: email is None, score is missing — both should be \N.
    bob_row = next(line for line in lines if line.startswith("2,Bob"))
    assert bob_row == "2,Bob,\\N,\\N"


def test_null_value_csv_preserves_literal_empty_string(tmp_path: Path):
    data = [{"id": 1, "note": ""}, {"id": 2}]
    src = tmp_path / "x.json"
    src.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "csv",
            "--columns",
            "id,note",
            "--null-value",
            "MISSING",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    # Strip the dry-run banner and the header row.
    body = result.output.split("id,note\n", 1)[1].strip().splitlines()
    # row 1 has literal "" → stays empty; row 2 has missing key → MISSING.
    assert body[0] == "1,"
    assert body[1] == "2,MISSING"


def test_null_value_sql_produces_quoted_literal(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "sql",
            "--table",
            "users",
            "--null-value",
            "\\N",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "'\\N'" in result.output
    assert ", NULL" not in result.output


# ── --no-header ───────────────────────────────────────────────────────────────


def test_no_header_omits_csv_header_row(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "csv",
            "--columns",
            "id,name",
            "--no-header",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    # Skip the dry-run banner line.
    body = "\n".join(result.output.strip().splitlines()[1:])
    # No header row — first data row should appear at the top of the body.
    assert body.startswith("1,Alice")
    assert "id,name" not in body


def test_header_default_includes_header(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "csv",
            "--columns",
            "id,name",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    # First line after the dry-run banner should be the header.
    body_first = result.output.strip().splitlines()[1]
    assert body_first == "id,name"


# ── --table, --include-create ─────────────────────────────────────────────────


def test_table_sets_target_table(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["convert", str(src), "--to", "sql", "--table", "custom_t", "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "INSERT INTO custom_t" in result.output


def test_include_create_emits_schema(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "sql",
            "--table",
            "users",
            "--include-create",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "CREATE TABLE IF NOT EXISTS users" in result.output


# ── --frontmatter ─────────────────────────────────────────────────────────────


def test_frontmatter_emits_yaml_block(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "markdown",
            "--frontmatter",
            "draft=false",
            "--frontmatter",
            "tag=users",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "---" in result.output
    assert "draft: false" in result.output or 'draft: "false"' in result.output
    assert "tag: users" in result.output


def test_frontmatter_with_equals_in_value(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "markdown",
            "--frontmatter",
            "equation=a=b+c",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0, result.output
    # First '=' splits — value retains 'a=b+c'.
    assert "a=b+c" in result.output


def test_flatten_sep_csv_uses_custom_separator(tmp_path: Path):
    data = [{"id": 1, "user": {"name": "Alice"}}]
    src = tmp_path / "x.json"
    src.write_text(json.dumps(data))
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["convert", str(src), "--to", "csv", "--flatten-sep", "_", "--dry-run"],
    )
    assert result.exit_code == 0, result.output
    assert "user_name" in result.output
    assert "user.name" not in result.output


def test_frontmatter_rejects_no_equals_token(tmp_path: Path):
    src = _write_input(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "convert",
            str(src),
            "--to",
            "markdown",
            "--frontmatter",
            "no_equals_here",
            "--dry-run",
        ],
    )
    assert result.exit_code != 0
    assert "key=val" in result.output
