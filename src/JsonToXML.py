import json
import xml.etree.ElementTree as ET
import html


class JsonToXML:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.root = ET.Element("root")  # Root element for the XML document

    def convert(self):
        for item in self.data:
            item_element = ET.SubElement(self.root, "item")
            self.add_elements(item, item_element)

    def add_elements(self, data, parent_element):
        for key, value in data.items():
            if isinstance(value, dict):
                sub_element = ET.SubElement(parent_element, key)
                self.add_elements(value, sub_element)
            elif isinstance(value, list):
                self.handle_list(value, parent_element, key)
            else:
                parent_element.set(key, str(value))

    def handle_list(self, data_list, parent_element, key):
        for item in data_list:
            list_element = ET.SubElement(
                parent_element, key[:-1]
            )  # Strip 's' and use as tag (simple plural to singular)
            if isinstance(item, dict):
                self.add_elements(item, list_element)
            else:
                list_element.text = str(item)

    def save_to_file(self, output_file):
        tree = ET.ElementTree(self.root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)


class JsonToXMLV2:
    def __init__(self, json_file):
        with open(json_file, "r") as file:
            self.data = json.load(file)
        self.root = ET.Element("root")  # Root element for the XML document

    def convert(self):
        for item in self.data:
            item_element = ET.SubElement(
                self.root, "item", code=item.get("code"), name=item.get("name")
            )
            self.add_description(item, item_element)
            self.handle_lists_and_dicts(item, item_element)

    def add_description(self, data, parent_element):
        description = ET.SubElement(parent_element, "description")
        description.text = html.escape(data.get("description", ""))

    def handle_lists_and_dicts(self, data, parent_element):
        for key, value in data.items():
            if key in ["code", "name", "description"]:
                continue  # These are already handled
            if isinstance(value, list):
                self.handle_list(value, parent_element, key)
            elif isinstance(value, dict):
                sub_element = ET.SubElement(parent_element, key)
                self.handle_lists_and_dicts(value, sub_element)

    def handle_list(self, data_list, parent_element, key):
        singular_key = (
            key[:-1] if key.endswith("s") else key
        )  # Handling plural to singular
        for item in data_list:
            list_element = ET.SubElement(parent_element, singular_key)
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, list):
                        self.handle_list(v, list_element, k)
                    elif isinstance(v, dict):
                        sub_element = ET.SubElement(list_element, k)
                        self.handle_lists_and_dicts(v, sub_element)
                    else:
                        list_element.set(k, html.escape(str(v)))
            else:
                list_element.text = html.escape(str(item))

    def save_to_file(self, output_file):
        tree = ET.ElementTree(self.root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
