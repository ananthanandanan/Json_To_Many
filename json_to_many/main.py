from .converters.markdown_converter import JsonToMarkdown
from .utils.file_utils import read_json_data
from .exceptions import UnsupportedFormatError
from .utils.constants import SUPPORTED_FORMATS


def convert(json_input, output_format, output_file=None, return_data=False):
    """
    Main entry point for converting JSON to various formats.

    :param json_input: Path to JSON file, a JSON string, or a Python data structure.
    :param output_format: Desired output format ('markdown', 'xml', 'csv').
    :param output_file: (Optional) Path to the output file.
    :param return_data: (Optional) If True, returns the converted data.
    :return: Converted data if return_data is True, else None.
    """

    data = read_json_data(json_input)

    if output_format.lower() == "markdown":
        converter = JsonToMarkdown(data)
    else:
        raise UnsupportedFormatError(
            f"Unsupported format: {output_format}. Supported formats are: {SUPPORTED_FORMATS}"
        )

    converter.converter()

    if output_file:
        converter.save_to_file(output_file)

    if return_data:
        return converter.markdown_lines
