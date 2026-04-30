import pytest
from json_to_many import convert


USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "score": 8.4},
    {"id": 2, "name": "Bob", "email": None, "score": 7.1},
]


# ── basic INSERT structure ────────────────────────────────────────────────────

def test_produces_insert_statement():
    result = convert(USERS, "sql", table="users")
    assert "INSERT INTO users" in result.data


def test_column_list_in_insert():
    result = convert(USERS, "sql", table="users")
    assert "(id, name, email, score)" in result.data


def test_values_are_in_output():
    result = convert(USERS, "sql", table="users")
    assert "'Alice'" in result.data
    assert "'alice@example.com'" in result.data


def test_none_becomes_null():
    result = convert(USERS, "sql", table="users")
    assert "NULL" in result.data


def test_single_dict_input():
    result = convert({"id": 1, "name": "Alice"}, "sql", table="users")
    assert "INSERT INTO users" in result.data
    assert "'Alice'" in result.data


# ── value escaping ────────────────────────────────────────────────────────────

def test_single_quotes_in_strings_are_escaped():
    data = [{"name": "O'Brien"}]
    result = convert(data, "sql", table="t")
    assert "O''Brien" in result.data


def test_bool_true_becomes_1():
    data = [{"active": True}]
    result = convert(data, "sql", table="t")
    assert "(1)" in result.data


def test_bool_false_becomes_0():
    data = [{"active": False}]
    result = convert(data, "sql", table="t")
    assert "(0)" in result.data


def test_float_value_preserved():
    data = [{"score": 8.4}]
    result = convert(data, "sql", table="t")
    assert "8.4" in result.data


# ── batch_size ────────────────────────────────────────────────────────────────

def test_batch_size_splits_into_multiple_inserts():
    data = [{"id": i} for i in range(5)]
    result = convert(data, "sql", table="t", batch_size=2)
    assert result.data.count("INSERT INTO t") == 3  # 2 + 2 + 1


def test_single_batch_when_records_fit():
    data = [{"id": i} for i in range(3)]
    result = convert(data, "sql", table="t", batch_size=10)
    assert result.data.count("INSERT INTO t") == 1


# ── include_create ────────────────────────────────────────────────────────────

def test_include_create_adds_create_table():
    result = convert(USERS, "sql", table="users", include_create=True)
    assert "CREATE TABLE IF NOT EXISTS users" in result.data


def test_create_table_before_insert():
    result = convert(USERS, "sql", table="users", include_create=True)
    create_pos = result.data.index("CREATE TABLE")
    insert_pos = result.data.index("INSERT INTO")
    assert create_pos < insert_pos


def test_create_table_infers_int_type():
    result = convert(USERS, "sql", table="users", include_create=True)
    assert "id INTEGER" in result.data


def test_create_table_infers_real_type():
    result = convert(USERS, "sql", table="users", include_create=True)
    assert "score REAL" in result.data


def test_create_table_infers_text_type():
    result = convert(USERS, "sql", table="users", include_create=True)
    assert "name TEXT" in result.data


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_rows_and_fields():
    result = convert(USERS, "sql", table="users")
    assert result.stats.rows == 2
    assert result.stats.fields == 4
