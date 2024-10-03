class JsonToManyError(Exception):
    """Base exception class for JsonToMany."""


class UnsupportedFormatError(JsonToManyError):
    """Exception raised for unsupported formats."""


class ConversionError(JsonToManyError):
    """Exception raised for errors during conversion."""
