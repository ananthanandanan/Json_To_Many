from .base_converter import BaseConverter
from ..utils.constants import DEFAULT_ENCODING


class JsonToMarkdown(BaseConverter):
    def __init__(self, data, **options):
        super().__init__(data, **options)
        self.markdown_lines = []
        self.converted_data = None

    def converter(self):
        title = self.options.get("title")
        if title is not None:
            self.markdown_lines.append(f"# {title}\n\n")
        self.parse_elements(self.data, 1)
        self.converted_data = "".join(self.markdown_lines)

    def parse_elements(self, element, level):
        if isinstance(element, dict):
            for key, value in element.items():
                self.add_heading(key, level)
                self.parse_elements(value, level + 1)
        elif isinstance(element, list):
            if self._is_list_of_primitives(element):
                self.add_primitive_list(element)
            else:
                for item in element:
                    self.parse_elements(item, level)
        else:
            self.add_text(element)

    def _is_list_of_primitives(self, lst):
        return len(lst) > 0 and all(
            not isinstance(x, (dict, list)) for x in lst
        )

    def add_heading(self, text, level):
        offset = self.options.get("heading_offset", 0)
        max_level = self.options.get("max_heading_level", 6)
        effective_level = max(1, level + offset)
        if effective_level <= max_level:
            self.markdown_lines.append(f"{'#' * effective_level} {text}\n\n")
        else:
            self.markdown_lines.append(f"**{text}**\n\n")

    def add_primitive_list(self, items):
        bullet_lists = self.options.get("bullet_lists", True)
        if bullet_lists:
            for item in items:
                self.markdown_lines.append(f"- {item}\n")
            self.markdown_lines.append("\n")
        else:
            for item in items:
                self.add_text(item)

    def add_text(self, text):
        self.markdown_lines.append(f"{text}\n\n")

    def save_to_file(self, file_name):
        with open(file_name, "w", encoding=DEFAULT_ENCODING) as file:
            file.writelines(self.markdown_lines)

    def get_converted_data(self):
        return self.converted_data
