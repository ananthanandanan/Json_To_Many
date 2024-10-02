# json_to_many/utils/file_utils.py
import json
from .constants import DEFAULT_ENCODING


def read_json_data(json_input):
    """
    Reads JSON data from a file path, a JSON string, or a Python data structure.

    :param json_input: Path to JSON file, a JSON string, or a Python data structure.
    :return: Parsed JSON data.
    """
    if isinstance(json_input, (dict, list)):
        return json_input
    try:
        # Try to read as a file path
        with open(json_input, "r", encoding=DEFAULT_ENCODING) as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If not a file or invalid JSON file, try to parse as JSON string
        return json.loads(json_input)
