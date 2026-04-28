import os
import tempfile
import unittest
from json_to_many.converters.xml_converter import JsonToXML
from json_to_many.result import ConversionResult


class TestJsonToXML(unittest.TestCase):
    def test_dict_conversion(self):
        data = {"name": "Alice", "age": "30"}
        converter = JsonToXML(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("<name>Alice</name>", result.data)
        self.assertIn("<age>30</age>", result.data)

    def test_nested_dict(self):
        data = {"person": {"name": "Bob", "city": "NYC"}}
        converter = JsonToXML(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("<person>", result.data)
        self.assertIn("<name>Bob</name>", result.data)
        self.assertIn("<city>NYC</city>", result.data)

    def test_list_of_dicts(self):
        data = [{"id": "1"}, {"id": "2"}]
        converter = JsonToXML(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertEqual(result.data.count("<id>"), 2)

    def test_returns_conversion_result(self):
        data = [{"x": "1"}, {"x": "2"}, {"x": "3"}]
        converter = JsonToXML(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIsInstance(result, ConversionResult)
        self.assertEqual(result.format, "xml")
        self.assertEqual(result.stats.rows, 3)
        self.assertEqual(result.stats.warnings, [])

    def test_dict_row_count(self):
        data = {"key": "value"}
        converter = JsonToXML(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertEqual(result.stats.rows, 1)

    def test_save_to_file(self):
        data = {"greeting": "hello"}
        converter = JsonToXML(data)
        converter.converter()
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name
        try:
            converter.save_to_file(path)
            with open(path, encoding="utf-8") as f:
                contents = f.read()
            self.assertIn("greeting", contents)
            self.assertIn("hello", contents)
        finally:
            os.unlink(path)

    def test_custom_root_element(self):
        converter = JsonToXML({"name": "Alice"}, root_element="person")
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("<person>", result.data)
        self.assertNotIn("<root>", result.data)

    def test_default_root_element(self):
        converter = JsonToXML({"x": "1"})
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("<root>", result.data)

    def test_pretty_print_adds_indentation(self):
        converter = JsonToXML({"a": "1", "b": "2"}, pretty_print=True)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("\n", result.data)
        self.assertIn("  ", result.data)

    def test_pretty_print_false_no_indentation(self):
        converter = JsonToXML({"a": "1"}, pretty_print=False)
        converter.converter()
        result = converter.get_converted_data()
        self.assertNotIn("\n  ", result.data)

    def test_item_element_wraps_list_items(self):
        converter = JsonToXML([{"id": "1"}, {"id": "2"}], item_element="item")
        converter.converter()
        result = converter.get_converted_data()
        self.assertEqual(result.data.count("<item>"), 2)
        self.assertEqual(result.data.count("</item>"), 2)

    def test_item_element_none_preserves_behavior(self):
        data = [{"id": "1"}, {"id": "2"}]
        r1 = JsonToXML(data)
        r1.converter()
        r2 = JsonToXML(data, item_element=None)
        r2.converter()
        self.assertEqual(r1.get_converted_data().data, r2.get_converted_data().data)

    def test_pretty_print_save_to_file(self):
        converter = JsonToXML({"greeting": "hello"}, pretty_print=True)
        converter.converter()
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            path = f.name
        try:
            converter.save_to_file(path)
            with open(path, encoding="utf-8") as f:
                contents = f.read()
            self.assertIn("\n", contents)
            self.assertIn("greeting", contents)
        finally:
            os.unlink(path)

    def test_all_xml_options_combined(self):
        converter = JsonToXML(
            [{"val": "a"}, {"val": "b"}],
            root_element="data",
            item_element="entry",
            pretty_print=True,
        )
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("<data>", result.data)
        self.assertEqual(result.data.count("<entry>"), 2)
        self.assertIn("\n", result.data)


if __name__ == "__main__":
    unittest.main()
