import json
from json_to_many import convert


# ── basic output ──────────────────────────────────────────────────────────────


def test_list_produces_one_line_per_record():
    data = [{"id": 1}, {"id": 2}, {"id": 3}]
    result = convert(data, "jsonl")
    lines = result.data.strip().splitlines()
    assert len(lines) == 3


def test_each_line_is_valid_json():
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = convert(data, "jsonl")
    for line in result.data.strip().splitlines():
        parsed = json.loads(line)
        assert "id" in parsed


def test_single_dict_produces_one_line():
    result = convert({"id": 1, "name": "Alice"}, "jsonl")
    lines = result.data.strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {"id": 1, "name": "Alice"}


def test_nested_dict_is_preserved():
    data = [{"user": {"name": "Alice", "city": "London"}}]
    result = convert(data, "jsonl")
    parsed = json.loads(result.data.strip())
    assert parsed["user"]["name"] == "Alice"


# ── options ───────────────────────────────────────────────────────────────────


def test_ensure_ascii_false_preserves_unicode():
    data = [{"name": "Ångström"}]
    result = convert(data, "jsonl", ensure_ascii=False)
    assert "Ångström" in result.data


def test_ensure_ascii_true_escapes_unicode():
    data = [{"name": "Ångström"}]
    result = convert(data, "jsonl", ensure_ascii=True)
    assert "Ångström" not in result.data
    assert "\\u" in result.data


# ── stats ─────────────────────────────────────────────────────────────────────


def test_stats_rows():
    data = [{"id": i} for i in range(5)]
    result = convert(data, "jsonl")
    assert result.stats.rows == 5
