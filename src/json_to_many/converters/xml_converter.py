from typing import Any
from .base_converter import BaseConverter
import xml.etree.ElementTree as ET
from ..utils.constants import DEFAULT_ENCODING
from ..result import ConversionResult, ConversionStats


class JsonToXML(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        root_element: str = self.options.get("root_element", "root")
        self.root = ET.Element(root_element)

    def converter(self) -> None:
        self.add_elements(self.data, self.root)
        if self.options.get("pretty_print", False):
            ET.indent(self.root, space="  ")
        rows = len(self.data) if isinstance(self.data, list) else 1
        self._stats = ConversionStats(rows=rows)

    def add_elements(
        self,
        data: dict | list | str | int | float | bool | None,
        parent: ET.Element,
    ) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                sub_element = ET.SubElement(parent, key)
                self.add_elements(value, sub_element)
        elif isinstance(data, list):
            item_tag: str | None = self.options.get("item_element", None)
            for item in data:
                if item_tag is not None:
                    wrapper = ET.SubElement(parent, item_tag)
                    self.add_elements(item, wrapper)
                else:
                    self.add_elements(item, parent)
        else:
            parent.text = str(data)

    def save_to_file(self, file_name: str) -> None:
        encoding = self.options.get("encoding", DEFAULT_ENCODING)
        xml_declaration: bool = self.options.get("xml_declaration", True)
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding=encoding, xml_declaration=xml_declaration)

    def get_converted_data(self) -> ConversionResult:
        xml_declaration: bool = self.options.get("xml_declaration", True)
        xml_str = ET.tostring(
            self.root,
            encoding=DEFAULT_ENCODING,
            xml_declaration=xml_declaration,
        ).decode(DEFAULT_ENCODING)
        return ConversionResult(data=xml_str, format="xml", stats=self._stats)
