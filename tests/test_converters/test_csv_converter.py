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

    def test_custom_delimiter(self):
        converter = JsonToCSV([{"a": "1", "b": "2"}], delimiter=";")
        converter.converter()
        result = converter.get_converted_data()
        lines = result.data.strip().splitlines()
        self.assertIn(";", lines[0])

    def test_custom_quotechar(self):
        converter = JsonToCSV([{"name": "Alice, Jr."}], quotechar="'")
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("'", result.data)

    def test_include_header_false(self):
        converter = JsonToCSV([{"x": "1", "y": "2"}], include_header=False)
        converter.converter()
        result = converter.get_converted_data()
        lines = result.data.strip().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertNotIn("x", lines[0])

    def test_include_header_true_default(self):
        converter = JsonToCSV([{"x": "1"}])
        converter.converter()
        result = converter.get_converted_data()
        lines = result.data.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("x", lines[0])

    def test_columns_explicit_ordering(self):
        converter = JsonToCSV([{"b": "2", "a": "1", "c": "3"}], columns=["a", "b", "c"])
        converter.converter()
        result = converter.get_converted_data()
        header = result.data.strip().splitlines()[0]
        self.assertEqual(header.strip(), "a,b,c")

    def test_columns_limits_output_columns(self):
        converter = JsonToCSV([{"a": "1", "b": "2", "c": "3"}], columns=["a", "c"])
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("a", result.data)
        self.assertIn("c", result.data)
        self.assertNotIn("b", result.data)
        self.assertEqual(result.stats.fields, 2)

    def test_columns_none_auto_detects(self):
        converter = JsonToCSV([{"a": "1", "b": "2"}], columns=None)
        converter.converter()
        result = converter.get_converted_data()
        self.assertIn("a", result.data)
        self.assertIn("b", result.data)

    def test_save_to_file_custom_encoding(self):
        data = [{"name": "Ångström", "value": "42"}]
        converter = JsonToCSV(data, encoding="utf-8")
        converter.converter()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            converter.save_to_file(path)
            with open(path, encoding="utf-8") as f:
                contents = f.read()
            self.assertIn("Ångström", contents)
        finally:
            os.unlink(path)

    def test_all_csv_options_combined(self):
        data = [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}]
        converter = JsonToCSV(
            data,
            delimiter="|",
            quotechar="'",
            include_header=False,
            columns=["name"],
        )
        converter.converter()
        result = converter.get_converted_data()
        lines = result.data.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("Alice", result.data)
        self.assertNotIn("role", result.data)


if __name__ == "__main__":
    unittest.main()
