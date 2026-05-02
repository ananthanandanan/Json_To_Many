from typing import Any

from .converters import JsonToMarkdown, JsonToXML, JsonToCSV
from .converters.html_converter import JsonToHTML
from .converters.jsonl_converter import JsonToJSONL
from .converters.sql_converter import JsonToSQL
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
}


def convert(
    json_input: str | dict | list,
    output_format: str,
    output_file: str | None = None,
    **options: Any,
) -> ConversionResult:
    """
    Main entry point for converting JSON to various formats.

    :param json_input: Path to JSON file, a JSON string, or a Python data structure.
    :param output_format: Desired output format ('markdown', 'xml', 'csv', 'html', 'jsonl', 'sql').
    :param output_file: (Optional) Path to the output file.
    :param options: Converter-specific options passed through to the converter.
    :return: ConversionResult with .data (string), .format, and .stats.
    """
    fmt = output_format.lower()

    converter_cls = _CONVERTERS.get(fmt)
    if converter_cls is None:
        raise UnsupportedFormatError(
            f"Unsupported format: {output_format}. Supported formats are: {SUPPORTED_FORMATS}"
        )

    data = read_json_data(json_input)

    config = load_config()
    merged = merge_options(config, fmt, options)

    converter = converter_cls(data, **merged)
    converter.converter()

    if output_file:
        converter.save_to_file(output_file)

    return converter.get_converted_data()
