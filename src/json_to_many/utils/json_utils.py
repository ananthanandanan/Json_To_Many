# json_to_many/utils/file_utils.py
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .constants import DEFAULT_ENCODING


def normalize_input(obj: Any) -> Any:
    """
    Recursively convert Pydantic-style models, dataclasses, and objects exposing
    ``to_dict()`` into plain dicts/lists. Duck-typed: no hard import of pydantic.

    Precedence: ``model_dump`` → dataclass → ``to_dict``.
    """
    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        return normalize_input(model_dump())
    if is_dataclass(obj) and not isinstance(obj, type):
        return normalize_input(asdict(obj))
    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return normalize_input(to_dict())
    if isinstance(obj, dict):
        return {key: normalize_input(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [normalize_input(item) for item in obj]
    return obj


def read_json_data(json_input: Any) -> dict | list:
    """
    Reads JSON data from a file path, a JSON string, a Python data structure,
    or an object that can be normalized (Pydantic model, dataclass, or any
    object with a ``to_dict()`` / ``model_dump()`` method).

    :param json_input: Path to JSON file, JSON string, dict/list, or a
        normalizable object (Pydantic model, dataclass, ``to_dict``-able).
    :return: Parsed JSON data.
    """
    normalised_data = normalize_input(json_input)
    if isinstance(normalised_data, (dict, list)):
        return normalised_data
    try:
        # Try to read as a file path
        with open(normalised_data, "r", encoding=DEFAULT_ENCODING) as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If not a file or invalid JSON file, try to parse as JSON string
        return json.loads(normalised_data)


def flatten_json(y: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Recursively flattens a nested JSON object.

    :param y: The JSON object to flatten.
    :param parent_key: The base key string.
    :param sep: The separator between keys.
    :return: A flat dictionary.
    """
    items = []
    for k, v in y.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ", ".join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)
