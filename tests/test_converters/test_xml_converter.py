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


if __name__ == "__main__":
    unittest.main()
