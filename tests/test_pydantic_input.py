"""Tests for normalize_input + Pydantic / dataclass / to_dict support in convert()."""

import dataclasses

import pytest

from json_to_many import analyze_schema, convert
from json_to_many.utils.json_utils import normalize_input


# ---------- Test doubles (duck-typed; no hard dep on pydantic for unit tests) ----------


class FakeModel:
    """Pydantic-shaped duck: exposes model_dump()."""

    def __init__(self, **values):
        self._values = values

    def model_dump(self):
        return dict(self._values)


class ToDictObj:
    def __init__(self, **values):
        self._values = values

    def to_dict(self):
        return dict(self._values)


@dataclasses.dataclass
class UserDC:
    id: int
    name: str


# ---------- normalize_input unit tests ----------


def test_normalize_plain_dict_passthrough():
    data = {"a": 1, "b": [1, 2, 3]}
    assert normalize_input(data) == data


def test_normalize_plain_list_passthrough():
    assert normalize_input([1, 2, 3]) == [1, 2, 3]


def test_normalize_pydantic_like_model():
    assert normalize_input(FakeModel(id=1, name="Alice")) == {"id": 1, "name": "Alice"}


def test_normalize_dataclass():
    assert normalize_input(UserDC(id=1, name="Alice")) == {"id": 1, "name": "Alice"}


def test_normalize_to_dict_object():
    assert normalize_input(ToDictObj(id=1, name="Alice")) == {"id": 1, "name": "Alice"}


def test_normalize_list_of_models():
    result = normalize_input([FakeModel(id=1), FakeModel(id=2)])
    assert result == [{"id": 1}, {"id": 2}]


def test_normalize_nested_model_in_dict():
    result = normalize_input({"user": FakeModel(id=1, name="Alice")})
    assert result == {"user": {"id": 1, "name": "Alice"}}


def test_normalize_model_with_nested_dict_field():
    result = normalize_input(FakeModel(id=1, profile={"city": "London"}))
    assert result == {"id": 1, "profile": {"city": "London"}}


def test_normalize_mixed_list():
    result = normalize_input(
        [FakeModel(id=1, name="A"), UserDC(id=2, name="B"), {"id": 3, "name": "C"}]
    )
    assert result == [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
        {"id": 3, "name": "C"},
    ]


def test_dataclass_with_to_dict_uses_asdict():
    """Precedence: is_dataclass beats to_dict, so asdict wins."""

    @dataclasses.dataclass
    class Tricky:
        id: int

        def to_dict(self):
            return {"wrong": "path"}

    assert normalize_input(Tricky(id=1)) == {"id": 1}


def test_model_dump_beats_dataclass():
    """Precedence: model_dump runs before dataclass check."""

    @dataclasses.dataclass
    class Hybrid:
        id: int

        def model_dump(self):
            return {"from": "model_dump"}

    assert normalize_input(Hybrid(id=1)) == {"from": "model_dump"}


def test_dataclass_class_itself_not_unwrapped():
    """is_dataclass returns True for the class object; the type guard prevents unwrap."""
    assert normalize_input(UserDC) is UserDC


def test_non_callable_model_dump_attribute_ignored():
    """A plain attribute called model_dump must not match — needs callable()."""

    class Decoy:
        model_dump = "not a method"

    obj = Decoy()
    assert normalize_input(obj) is obj


# ---------- End-to-end convert() integration ----------


def test_convert_single_model_to_csv():
    result = convert(FakeModel(id=1, name="Alice"), "csv")
    assert "id" in result.data
    assert "Alice" in result.data
    assert result.stats.rows == 1


def test_convert_list_of_dataclasses_to_csv():
    result = convert([UserDC(id=1, name="Alice"), UserDC(id=2, name="Bob")], "csv")
    assert "Alice" in result.data
    assert "Bob" in result.data
    assert result.stats.rows == 2


def test_convert_mixed_list_to_markdown():
    result = convert(
        [FakeModel(id=1, name="Alice"), UserDC(id=2, name="Bob")],
        "markdown",
    )
    assert "Alice" in result.data
    assert "Bob" in result.data


def test_analyze_schema_accepts_models():
    schema = analyze_schema(
        [FakeModel(id=1, name="Alice"), FakeModel(id=2, name="Bob")]
    )
    field_names = {f.name for f in schema.fields}
    assert {"id", "name"} <= field_names


# ---------- Real Pydantic v2 (skipped if not installed) ----------

pydantic = pytest.importorskip("pydantic")


def test_real_pydantic_v2_model():
    class User(pydantic.BaseModel):
        id: int
        name: str

    result = convert([User(id=1, name="Alice"), User(id=2, name="Bob")], "csv")
    assert "Alice" in result.data
    assert "Bob" in result.data
    assert result.stats.rows == 2


def test_real_pydantic_nested_model():
    class Profile(pydantic.BaseModel):
        city: str

    class User(pydantic.BaseModel):
        id: int
        profile: Profile

    result = convert(User(id=1, profile=Profile(city="London")), "csv")
    assert "profile.city" in result.data
    assert "London" in result.data
