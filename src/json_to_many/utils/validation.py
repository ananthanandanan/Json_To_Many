# json_to_many/utils/validation.py
def validate_json(data: object) -> bool:
    """
    Validates if the input data is valid JSON.

    :param data: Data to validate.
    :return: Boolean indicating validity.
    """
    try:
        if isinstance(data, dict) or isinstance(data, list):
            return True
        else:
            raise ValueError("Data is not a valid JSON object or array.")
    except Exception as e:
        raise ValueError(f"Invalid JSON data: {e}")
