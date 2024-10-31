from .base_converter import BaseConverter
import xml.etree.ElementTree as ET
from ..utils.constants import DEFAULT_ENCODING


class JsonToXML(BaseConverter):
    def __init__(self, data):
        super().__init__(data)
        self.root = ET.Element("root")

    def converter(self):
        self.add_elements(self.data, self.root)

    def add_elements(self, data, parent):
        """
        Recursively add elements to the XML tree.

        :param data: JSON data to be converted.
        :param parent: Parent XML element.
        """

        if isinstance(data, dict):
            for key, value in data.items():
                sub_element = ET.SubElement(parent, key)
                self.add_elements(value, sub_element)
        elif isinstance(data, list):
            for item in data:
                self.add_elements(item, parent)
        else:
            parent.text = str(data)

    def save_to_file(self, file_name):
        tree = ET.ElementTree(self.root)
        tree.write(file_name, encoding=DEFAULT_ENCODING, xml_declaration=True)

    def get_converted_data(self):
        return ET.tostring(self.root, encoding=DEFAULT_ENCODING).decode(
            DEFAULT_ENCODING
        )
