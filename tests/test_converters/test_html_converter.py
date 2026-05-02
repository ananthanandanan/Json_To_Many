from json_to_many import convert


FLAT_RECORDS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
]
SINGLE_DICT = {"name": "Alice", "age": 30}
NESTED = {"user": {"name": "Alice", "city": "London"}}


# ── list of dicts → table ─────────────────────────────────────────────────────


def test_list_of_dicts_renders_table():
    result = convert(FLAT_RECORDS, "html")
    assert "<table" in result.data
    assert "<thead>" in result.data
    assert "<tbody>" in result.data


def test_table_headers_match_keys():
    result = convert(FLAT_RECORDS, "html")
    assert "<th>id</th>" in result.data
    assert "<th>name</th>" in result.data
    assert "<th>email</th>" in result.data


def test_table_rows_contain_values():
    result = convert(FLAT_RECORDS, "html")
    assert "<td>Alice</td>" in result.data
    assert "<td>2</td>" in result.data


def test_sparse_field_renders_empty_cell():
    data = [{"id": 1, "name": "Alice"}, {"id": 2}]
    result = convert(data, "html")
    assert "<td></td>" in result.data


# ── table_style ───────────────────────────────────────────────────────────────


def test_table_style_none_has_no_class():
    result = convert(FLAT_RECORDS, "html", table_style="none")
    assert "class=" not in result.data


def test_table_style_github_adds_class():
    result = convert(FLAT_RECORDS, "html", table_style="github")
    assert 'class="table"' in result.data


def test_table_style_bootstrap_adds_class():
    result = convert(FLAT_RECORDS, "html", table_style="bootstrap")
    assert "table-striped" in result.data


# ── dict → definition list ────────────────────────────────────────────────────


def test_single_dict_renders_dl():
    result = convert(SINGLE_DICT, "html")
    assert "<dl>" in result.data
    assert "<dt>name</dt>" in result.data
    assert "<dd>Alice</dd>" in result.data


def test_nested_dict_renders_nested_dl():
    result = convert(NESTED, "html")
    assert "<dl>" in result.data
    assert "<dt>user</dt>" in result.data
    assert "<dt>name</dt>" in result.data


# ── wrap_in_page ──────────────────────────────────────────────────────────────


def test_wrap_in_page_adds_html_scaffold():
    result = convert(FLAT_RECORDS, "html", wrap_in_page=True)
    assert "<!DOCTYPE html>" in result.data
    assert "<html>" in result.data
    assert "<body>" in result.data


def test_wrap_in_page_with_title():
    result = convert(FLAT_RECORDS, "html", wrap_in_page=True, title="My Report")
    assert "<title>My Report</title>" in result.data


def test_bootstrap_cdn_only_in_wrapped_page():
    result = convert(FLAT_RECORDS, "html", table_style="bootstrap", wrap_in_page=True)
    assert "bootstrap" in result.data
    assert "<head>" in result.data


# ── html escaping ─────────────────────────────────────────────────────────────


def test_html_special_chars_are_escaped():
    data = [{"name": "<script>alert('xss')</script>"}]
    result = convert(data, "html")
    assert "<script>" not in result.data
    assert "&lt;script&gt;" in result.data


# ── stats ─────────────────────────────────────────────────────────────────────


def test_stats_rows_and_fields():
    result = convert(FLAT_RECORDS, "html")
    assert result.stats.rows == 2
    assert result.stats.fields == 3
