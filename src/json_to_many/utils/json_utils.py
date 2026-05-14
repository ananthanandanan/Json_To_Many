# json_to_many/utils/file_utils.py
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .constants import DEFAULT_ENCODING


def normalize_json_data(json_input: Any) -> Any:
    if hasattr(json_input, "model_dump"):
        return normalize_json_data(json_input.model_dump())
    if is_dataclass(json_input) and not isinstance(json_input, type):
        return normalize_json_data(asdict(json_input))
    if isinstance(json_input, list):
        return [normalize_json_data(item) for item in json_input]
    if isinstance(json_input, dict):
        return {key: normalize_json_data(value) for key, value in json_input.items()}
    return json_input


def read_json_data(json_input: str | dict | list) -> dict | list:
    """
    Reads JSON data from a file path, a JSON string, or a Python data structure.

    :param json_input: Path to JSON file, a JSON string, or a Python data structure.
    :return: Parsed JSON data.
    """
    json_input = normalize_json_data(json_input)
    if isinstance(json_input, (dict, list)):
        return json_input
    try:
        # Try to read as a file path
        with open(json_input, "r", encoding=DEFAULT_ENCODING) as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If not a file or invalid JSON file, try to parse as JSON string
        return json.loads(json_input)


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
