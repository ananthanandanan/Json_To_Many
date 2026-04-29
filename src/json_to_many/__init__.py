# json_to_many/__init__.py
from .main import convert
from .result import ConversionResult, ConversionStats
from .exceptions import JsonToManyError, UnsupportedFormatError
from .utils.schema import analyze_schema, SchemaResult, FieldInfo

__all__ = [
    "convert",
    "ConversionResult",
    "ConversionStats",
    "JsonToManyError",
    "UnsupportedFormatError",
    "analyze_schema",
    "SchemaResult",
    "FieldInfo",
]
