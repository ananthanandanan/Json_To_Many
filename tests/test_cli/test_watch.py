from __future__ import annotations

import json
import os
from pathlib import Path

from click.testing import CliRunner

from json_to_many.cli.commands.watch import _discover, _run_once
from json_to_many.cli.main import cli

USERS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


def _collector():
    """Return (log_fn, lines) where log_fn appends to the captured list."""
    lines: list[str] = []
    return lines.append, lines


# ── _discover ───────────────────────────────────────────────────────────────


def test_discover_single_file_passthrough(tmp_path: Path):
    src = tmp_path / "users.json"
    src.write_text(json.dumps(USERS))
    assert _discover(str(src), None) == [str(src)]


def test_discover_directory_finds_all_input_formats(tmp_path: Path):
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.csv").write_text("x\n1")
    (tmp_path / "c.txt").write_text("ignored")
    found = _discover(str(tmp_path), None)
    assert found == sorted([str(tmp_path / "a.json"), str(tmp_path / "b.csv")])


def test_discover_directory_respects_from_format(tmp_path: Path):
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.csv").write_text("x\n1")
    assert _discover(str(tmp_path), "json") == [str(tmp_path / "a.json")]


# ── _run_once ─────────────────────────────────────────────────────────────────


def test_run_once_builds_changed_then_skips_unchanged(tmp_path: Path):
    src = tmp_path / "users.json"
    src.write_text(json.dumps(USERS))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    log, lines = _collector()
    mtimes: dict[str, float] = {}

    built = _run_once(str(src), mtimes, ("markdown",), str(out_dir), None, {}, log)
    assert built == 1
    assert (out_dir / "users.md").exists()
    assert len(lines) == 1

    # Second pass with no change: nothing rebuilt, nothing logged.
    built = _run_once(str(src), mtimes, ("markdown",), str(out_dir), None, {}, log)
    assert built == 0
    assert len(lines) == 1


def test_run_once_rebuilds_after_mtime_change(tmp_path: Path):
    src = tmp_path / "users.json"
    src.write_text(json.dumps(USERS))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    log, _ = _collector()
    mtimes: dict[str, float] = {}

    _run_once(str(src), mtimes, ("markdown",), str(out_dir), None, {}, log)
    # Bump mtime to simulate a save.
    future = os.stat(src).st_mtime + 10
    os.utime(src, (future, future))

    built = _run_once(str(src), mtimes, ("markdown",), str(out_dir), None, {}, log)
    assert built == 1


def test_run_once_multiple_formats(tmp_path: Path):
    src = tmp_path / "users.json"
    src.write_text(json.dumps(USERS))
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    log, _ = _collector()

    built = _run_once(str(src), {}, ("markdown", "csv"), str(out_dir), None, {}, log)
    assert built == 2
    assert (out_dir / "users.md").exists()
    assert (out_dir / "users.csv").exists()


def test_run_once_renders_openapi_template(tmp_path: Path):
    fixture = Path(__file__).parent.parent / "fixtures" / "openapi" / "petstore.json"
    src = tmp_path / "petstore.json"
    src.write_text(fixture.read_text())
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    log, _ = _collector()

    _run_once(
        str(src),
        {},
        ("markdown",),
        str(out_dir),
        None,
        {"template": "openapi"},
        log,
    )
    rendered = (out_dir / "petstore.md").read_text()
    assert rendered.startswith("# Petstore API")
    assert "## Schemas" in rendered


def test_run_once_bad_file_is_logged_not_raised(tmp_path: Path):
    src = tmp_path / "broken.json"
    src.write_text("{not valid json")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    log, lines = _collector()

    # Should not raise; error is logged and the pass continues.
    built = _run_once(str(src), {}, ("markdown",), str(out_dir), None, {}, log)
    assert built == 0
    assert any("ERROR" in line for line in lines)


# ── CLI surface ───────────────────────────────────────────────────────────────


def test_watch_missing_source_errors(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["watch", str(tmp_path / "nope.json"), "--to", "markdown", "-d", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "No such file or directory" in result.output


def test_watch_empty_directory_errors(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    runner = CliRunner()
    result = runner.invoke(
        cli, ["watch", str(empty), "--to", "markdown", "-d", str(tmp_path / "out")]
    )
    assert result.exit_code != 0
    assert "No input files found" in result.output


def test_watch_registered():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert "watch" in result.output
