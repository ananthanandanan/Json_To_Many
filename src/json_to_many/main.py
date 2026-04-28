from typing import Any
from .converters import JsonToMarkdown
from .converters import JsonToXML
from .converters import JsonToCSV
from .utils import read_json_data
from .exceptions import UnsupportedFormatError
from .utils import SUPPORTED_FORMATS
from .result import ConversionResult


def convert(
    json_input: str | dict | list,
    output_format: str,
    output_file: str | None = None,
    **options: Any,
) -> ConversionResult:
    """
    Main entry point for converting JSON to various formats.

    :param json_input: Path to JSON file, a JSON string, or a Python data structure.
    :param output_format: Desired output format ('markdown', 'xml', 'csv').
    :param output_file: (Optional) Path to the output file.
    :param options: Converter-specific options passed through to the converter.
    :return: ConversionResult with .data (string), .format, and .stats.
    """

    data = read_json_data(json_input)

    if output_format.lower() == "markdown":
        converter = JsonToMarkdown(data, **options)
    elif output_format.lower() == "xml":
        converter = JsonToXML(data, **options)
    elif output_format.lower() == "csv":
        converter = JsonToCSV(data, **options)
    else:
        raise UnsupportedFormatError(
            f"Unsupported format: {output_format}. Supported formats are: {SUPPORTED_FORMATS}"
        )

    converter.converter()

    if output_file:
        converter.save_to_file(output_file)

    return converter.get_converted_data()
