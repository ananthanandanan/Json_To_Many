from __future__ import annotations

import json
import unittest

from json_to_many.converters.json_converter import JsonFormatter
from json_to_many.result import ConversionResult


class TestJsonFormatter(unittest.TestCase):
    def test_list_of_dicts(self):
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        formatter = JsonFormatter(data)
        formatter.converter()
        result = formatter.get_converted_data()
        self.assertEqual(json.loads(result.data), data)
        self.assertEqual(result.format, "json")
        self.assertEqual(result.stats.rows, 2)
        self.assertEqual(result.stats.fields, 2)

    def test_single_dict(self):
        data = {"id": 1, "name": "Alice"}
        formatter = JsonFormatter(data)
        formatter.converter()
        result = formatter.get_converted_data()
        self.assertEqual(json.loads(result.data), data)
        self.assertEqual(result.stats.rows, 1)
        self.assertEqual(result.stats.fields, 2)

    def test_indent_option(self):
        data = {"a": 1}
        formatter = JsonFormatter(data, indent=4)
        formatter.converter()
        self.assertIn('\n    "a": 1', formatter.get_converted_data().data)

    def test_sort_keys_option(self):
        data = {"b": 2, "a": 1}
        formatter = JsonFormatter(data, sort_keys=True)
        formatter.converter()
        out = formatter.get_converted_data().data
        self.assertLess(out.index('"a"'), out.index('"b"'))

    def test_ensure_ascii_default_false(self):
        data = {"name": "日本語"}
        formatter = JsonFormatter(data)
        formatter.converter()
        self.assertIn("日本語", formatter.get_converted_data().data)

    def test_ensure_ascii_true(self):
        data = {"name": "日本語"}
        formatter = JsonFormatter(data, ensure_ascii=True)
        formatter.converter()
        self.assertNotIn("日本語", formatter.get_converted_data().data)

    def test_returns_conversion_result(self):
        formatter = JsonFormatter([{"a": 1}])
        formatter.converter()
        self.assertIsInstance(formatter.get_converted_data(), ConversionResult)


if __name__ == "__main__":
    unittest.main()
