from __future__ import annotations


def infer_type(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "object"
    return "str"


def coerce_string(
    value: str, null_values: tuple[str, ...] | list[str] = ("", "N/A", "NULL")
) -> object:
    """Per-cell string → typed Python value. Order matters: int before float
    so "42" stays int; strict bool so "1"/"0" stay as int and "yes"/"no" as str.
    """
    if value in null_values:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value
