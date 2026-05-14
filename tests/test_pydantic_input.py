from dataclasses import dataclass

from json_to_many import convert


class FakePydanticModel:
    def __init__(self, **values):
        self.values = values

    def model_dump(self):
        return self.values


@dataclass
class UserDataclass:
    id: int
    name: str


def test_convert_single_model_to_csv():
    result = convert(FakePydanticModel(id=1, name="Alice"), "csv")

    assert "id" in result.data
    assert "name" in result.data
    assert "Alice" in result.data
    assert result.stats.rows == 1


def test_convert_list_of_models_to_csv():
    result = convert(
        [FakePydanticModel(id=1, name="Alice"), FakePydanticModel(id=2, name="Bob")],
        "csv",
    )

    assert "Alice" in result.data
    assert "Bob" in result.data
    assert result.stats.rows == 2


def test_convert_nested_model_to_csv():
    result = convert(FakePydanticModel(id=1, profile={"city": "London"}), "csv")

    assert "profile.city" in result.data
    assert "London" in result.data


def test_convert_dataclass_to_csv():
    result = convert(UserDataclass(id=1, name="Alice"), "csv")

    assert "Alice" in result.data
    assert result.stats.rows == 1


def test_convert_mixed_list_to_csv():
    result = convert(
        [FakePydanticModel(id=1, name="Alice"), UserDataclass(id=2, name="Bob")],
        "csv",
    )

    assert "Alice" in result.data
    assert "Bob" in result.data
    assert result.stats.rows == 2
