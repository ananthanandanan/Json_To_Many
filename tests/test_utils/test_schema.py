import pytest
from json_to_many.utils.schema import analyze_schema, FieldInfo, SchemaResult


# ── helpers ──────────────────────────────────────────────────────────────────

def field_by_name(result: SchemaResult, name: str) -> FieldInfo:
    return next(f for f in result.fields if f.name == name)


# ── basic structure ───────────────────────────────────────────────────────────

def test_flat_list_of_dicts():
    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    result = analyze_schema(data)

    assert result.record_count == 2
    assert len(result.fields) == 2

    id_field = field_by_name(result, "id")
    assert id_field.type == "int"
    assert id_field.coverage == 100.0

    name_field = field_by_name(result, "name")
    assert name_field.type == "str"
    assert name_field.coverage == 100.0


def test_single_dict_input():
    data = {"id": 1, "name": "Alice"}
    result = analyze_schema(data)

    assert result.record_count == 1
    assert len(result.fields) == 2
    assert field_by_name(result, "id").coverage == 100.0


def test_empty_list():
    result = analyze_schema([])
    assert result.record_count == 0
    assert result.fields == []


# ── nested keys ───────────────────────────────────────────────────────────────

def test_nested_dict_dot_notation():
    data = [{"id": 1, "address": {"city": "London", "zip": "SW1A"}}]
    result = analyze_schema(data)

    names = {f.name for f in result.fields}
    assert "address.city" in names
    assert "address.zip" in names
    assert "address" not in names


# ── coverage ─────────────────────────────────────────────────────────────────

def test_sparse_field_coverage():
    data = [
        {"id": 1, "email": "a@example.com"},
        {"id": 2},
        {"id": 3},
        {"id": 4},
    ]
    result = analyze_schema(data)

    email_field = field_by_name(result, "email")
    assert email_field.coverage == 25.0


def test_fields_sorted_by_coverage_desc():
    data = [
        {"id": 1, "email": "a@example.com"},
        {"id": 2},
        {"id": 3},
    ]
    result = analyze_schema(data)
    coverages = [f.coverage for f in result.fields]
    assert coverages == sorted(coverages, reverse=True)


# ── type inference ────────────────────────────────────────────────────────────

def test_bool_distinguished_from_int():
    data = [{"flag": True}, {"flag": False}]
    result = analyze_schema(data)
    assert field_by_name(result, "flag").type == "bool"


def test_int_type():
    result = analyze_schema([{"x": 42}])
    assert field_by_name(result, "x").type == "int"


def test_float_type():
    result = analyze_schema([{"score": 8.4}])
    assert field_by_name(result, "score").type == "float"


def test_list_type():
    result = analyze_schema([{"tags": ["admin", "user"]}])
    # flatten_json converts lists to comma-separated strings, so type is str
    assert field_by_name(result, "tags").type == "str"


def test_null_only_field():
    data = [{"id": 1, "deleted_at": None}, {"id": 2, "deleted_at": None}]
    result = analyze_schema(data)
    assert field_by_name(result, "deleted_at").type == "null"


def test_mixed_type_field():
    data = [{"value": 1}, {"value": "one"}, {"value": 1.5}]
    result = analyze_schema(data)
    assert field_by_name(result, "value").type == "mixed"


# ── null does not pollute type resolution ─────────────────────────────────────

def test_null_does_not_make_field_mixed():
    # Some records have None, some have int — should resolve to "int", not "mixed"
    data = [{"score": 10}, {"score": None}, {"score": 7}]
    result = analyze_schema(data)
    assert field_by_name(result, "score").type == "int"


def test_null_coverage_reflects_presence_not_value():
    # Field exists in all records but is None in some — coverage should be 100%
    data = [{"score": 10}, {"score": None}]
    result = analyze_schema(data)
    assert field_by_name(result, "score").coverage == 100.0


# ── samples ───────────────────────────────────────────────────────────────────

def test_sample_is_first_non_null_value():
    data = [{"name": None}, {"name": "Alice"}, {"name": "Bob"}]
    result = analyze_schema(data)
    assert field_by_name(result, "name").sample == '"Alice"'


def test_sample_null_when_all_values_are_null():
    data = [{"x": None}, {"x": None}]
    result = analyze_schema(data)
    assert field_by_name(result, "x").sample == "null"


# ── public API surface ────────────────────────────────────────────────────────

def test_importable_from_top_level():
    from json_to_many import analyze_schema as fn, SchemaResult as SR, FieldInfo as FI
    assert callable(fn)
    assert SR is SchemaResult
    assert FI is FieldInfo
