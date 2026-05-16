import os
from typing import Any

from .converters import JsonToMarkdown, JsonToXML, JsonToCSV
from .converters.html_converter import JsonToHTML
from .converters.json_converter import JsonFormatter
from .converters.jsonl_converter import JsonToJSONL
from .converters.sql_converter import JsonToSQL
from .readers.csv_reader import read_csv, CSV_READER_OPTIONS
from .utils import read_json_data
from .exceptions import UnsupportedFormatError
from .utils import SUPPORTED_FORMATS
from .result import ConversionResult
from .config import load_config, merge_options

_CONVERTERS = {
    "markdown": JsonToMarkdown,
    "xml": JsonToXML,
    "csv": JsonToCSV,
    "html": JsonToHTML,
    "jsonl": JsonToJSONL,
    "sql": JsonToSQL,
    "json": JsonFormatter,
}

_READERS = {
    "csv": read_csv,
}


def _detect_input_format(json_input: Any, from_format: str | None) -> str | None:
    if from_format is not None:
        return from_format.lower()
    if isinstance(json_input, str) and os.path.exists(json_input):
        ext = os.path.splitext(json_input)[1].lower().lstrip(".")
        if ext in _READERS:
            return ext
    return None


def convert(
    json_input: str | dict | list,
    output_format: str,
    output_file: str | None = None,
    *,
    from_format: str | None = None,
    **options: Any,
) -> ConversionResult:
    """
    Main entry point for converting structured data to various formats.

    :param json_input: Path to a JSON/CSV file, a JSON/CSV string, or a Python
        data structure (dict, list, Pydantic model, dataclass, to_dict-able).
    :param output_format: Desired output format ('markdown', 'xml', 'csv',
        'html', 'jsonl', 'sql', 'json').
    :param output_file: (Optional) Path to the output file.
    :param from_format: (Optional) Explicit input format ('csv', 'json'). When
        omitted, file paths dispatch by extension and other inputs default to
        JSON.
    :param options: Converter/reader options passed through.
    :return: ConversionResult with .data (string), .format, and .stats.
    """
    fmt = output_format.lower()

    converter_cls = _CONVERTERS.get(fmt)
    if converter_cls is None:
        raise UnsupportedFormatError(
            f"Unsupported format: {output_format}. Supported formats are: {SUPPORTED_FORMATS}"
        )

    src_fmt = _detect_input_format(json_input, from_format)

    if src_fmt == "csv":
        reader_opts = {
            k: options.pop(k) for k in list(options) if k in CSV_READER_OPTIONS
        }
        data = read_csv(json_input, **reader_opts)
    elif src_fmt in (None, "json"):
        data = read_json_data(json_input)
    else:
        raise UnsupportedFormatError(
            f"Unsupported input format: {src_fmt}. Supported input formats are: json, csv"
        )

    config = load_config()
    merged = merge_options(config, fmt, options)

    converter = converter_cls(data, **merged)
    converter.converter()

    if output_file:
        converter.save_to_file(output_file)

    return converter.get_converted_data()
