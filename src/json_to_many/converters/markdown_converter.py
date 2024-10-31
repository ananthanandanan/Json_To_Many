from .base_converter import BaseConverter
from ..utils.constants import DEFAULT_ENCODING


class JsonToMarkdown(BaseConverter):
    def __init__(self, data):
        super().__init__(data)
        self.markdown_lines = []
        self.converted_data = None

    def converter(self):
        self.parse_elements(self.data, 1)
        self.converted_data = "".join(self.markdown_lines)

    def parse_elements(self, element, level):
        if isinstance(element, dict):
            for key, value in element.items():
                self.add_heading(key, level)
                self.parse_elements(value, level + 1)
        elif isinstance(element, list):
            for item in element:
                self.parse_elements(item, level)
        else:
            self.add_text(element)

    def add_heading(self, text, level):
        self.markdown_lines.append(f"{'#' * level} {text}\n\n")

    def add_text(self, text):
        self.markdown_lines.append(f"{text}\n\n")

    def save_to_file(self, file_name):
        with open(file_name, "w", encoding=DEFAULT_ENCODING) as file:
            file.writelines(self.markdown_lines)

    def get_converted_data(self):
        return self.converted_data
