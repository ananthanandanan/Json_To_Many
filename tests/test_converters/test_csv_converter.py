import os
import tempfile
import unittest
from json_to_many.converters.csv_converter import JsonToCSV
from json_to_many.result import ConversionResult


class TestJsonToCSV(unittest.TestCase):
    def test_list_of_dicts(self):
        data = [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]
        converter = JsonToCSV(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("name", result.data)
        self.assertIn("role", result.data)
        self.assertIn("Alice", result.data)
        self.assertIn("Bob", result.data)

    def test_single_dict(self):
        data = {"id": "1", "value": "x"}
        converter = JsonToCSV(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("id", result.data)
        self.assertIn("value", result.data)
        self.assertIn("1", result.data)

    def test_nested_dict_flattened(self):
        data = [{"user": {"name": "Carol", "age": "25"}}]
        converter = JsonToCSV(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("user.name", result.data)
        self.assertIn("user.age", result.data)
        self.assertIn("Carol", result.data)

    def test_returns_conversion_result(self):
        data = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
        converter = JsonToCSV(data)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIsInstance(result, ConversionResult)
        self.assertEqual(result.format, "csv")
        self.assertEqual(result.stats.rows, 3)
        self.assertEqual(result.stats.fields, 1)
        self.assertEqual(result.stats.warnings, [])

    def test_missing_fields_filled(self):
        data = [{"a": "1", "b": "2"}, {"a": "3"}]
        converter = JsonToCSV(data)
        converter.converter()
        result = converter.get_converted_data()
        lines = result.data.strip().splitlines()
        # header + 2 data rows
        self.assertEqual(len(lines), 3)
        # second row should have empty field for missing key
        self.assertIn(",", lines[2])

    def test_save_to_file(self):
        data = [{"x": "10", "y": "20"}]
        converter = JsonToCSV(data)
        converter.converter()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            converter.save_to_file(path)
            with open(path, encoding="utf-8") as f:
                contents = f.read()
            self.assertIn("x", contents)
            self.assertIn("10", contents)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
