import os
import tempfile
import textwrap

import pytest

from json_to_many.config import load_config, merge_options


def _write_toml(directory: str, content: str) -> str:
    path = os.path.join(directory, ".json2many.toml")
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))
    return path


# ── load_config ───────────────────────────────────────────────────────────────

def test_returns_empty_dict_when_no_config():
    with tempfile.TemporaryDirectory() as d:
        result = load_config(d)
    assert result == {}


def test_loads_config_from_start_dir():
    with tempfile.TemporaryDirectory() as d:
        _write_toml(d, """
            [converters.csv]
            delimiter = ";"
        """)
        result = load_config(d)
    assert result["converters"]["csv"]["delimiter"] == ";"


def test_walks_up_to_find_config():
    with tempfile.TemporaryDirectory() as root:
        _write_toml(root, """
            [converters.xml]
            pretty_print = true
        """)
        nested = os.path.join(root, "a", "b")
        os.makedirs(nested)
        result = load_config(nested)
    assert result["converters"]["xml"]["pretty_print"] is True


def test_loads_defaults_section():
    with tempfile.TemporaryDirectory() as d:
        _write_toml(d, """
            [defaults]
            encoding = "latin-1"
        """)
        result = load_config(d)
    assert result["defaults"]["encoding"] == "latin-1"


# ── merge_options ─────────────────────────────────────────────────────────────

def test_explicit_options_win_over_config():
    config = {"converters": {"csv": {"delimiter": ";"}}}
    merged = merge_options(config, "csv", {"delimiter": ","})
    assert merged["delimiter"] == ","


def test_format_config_fills_in_missing_options():
    config = {"converters": {"csv": {"delimiter": ";", "sort_columns": True}}}
    merged = merge_options(config, "csv", {})
    assert merged["delimiter"] == ";"
    assert merged["sort_columns"] is True


def test_defaults_are_applied_as_base():
    config = {"defaults": {"encoding": "latin-1"}, "converters": {}}
    merged = merge_options(config, "csv", {})
    assert merged["encoding"] == "latin-1"


def test_priority_order_defaults_then_format_then_explicit():
    config = {
        "defaults": {"encoding": "latin-1", "delimiter": "|"},
        "converters": {"csv": {"delimiter": ";"}},
    }
    merged = merge_options(config, "csv", {"delimiter": ","})
    assert merged["encoding"] == "latin-1"   # from defaults
    assert merged["delimiter"] == ","         # explicit wins over format config


def test_empty_config_returns_explicit_options_unchanged():
    merged = merge_options({}, "csv", {"delimiter": "\t"})
    assert merged == {"delimiter": "\t"}
