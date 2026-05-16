from __future__ import annotations

import json
import os
import tempfile
import unittest

from json_to_many import convert
from json_to_many.converters.csv_converter import JsonToCSV
from json_to_many.readers.csv_reader import read_csv


class TestCsvReader(unittest.TestCase):
    def test_basic_typed_inference(self):
        csv_text = "id,name,score\n1,Alice,8.4\n2,Bob,7.1\n"
        records = read_csv(csv_text)
        self.assertEqual(
            records,
            [
                {"id": 1, "name": "Alice", "score": 8.4},
                {"id": 2, "name": "Bob", "score": 7.1},
            ],
        )

    def test_bool_strict(self):
        csv_text = "id,active,flag\n1,true,1\n2,FALSE,0\n3,yes,no\n"
        records = read_csv(csv_text)
        # bools only from literal true/false (any case); 1/0 stay int, yes/no stay str.
        self.assertEqual(records[0], {"id": 1, "active": True, "flag": 1})
        self.assertEqual(records[1], {"id": 2, "active": False, "flag": 0})
        self.assertEqual(records[2], {"id": 3, "active": "yes", "flag": "no"})

    def test_null_default_tokens(self):
        csv_text = "id,name,note\n1,Alice,\n2,N/A,NULL\n"
        records = read_csv(csv_text)
        self.assertIsNone(records[0]["note"])
        self.assertIsNone(records[1]["name"])
        self.assertIsNone(records[1]["note"])

    def test_custom_null_values(self):
        csv_text = "id,name\n1,unknown\n2,Bob\n"
        records = read_csv(csv_text, null_values=["unknown"])
        self.assertIsNone(records[0]["name"])
        self.assertEqual(records[1]["name"], "Bob")
        # default tokens no longer apply when overridden
        records2 = read_csv("id,name\n1,\n", null_values=["unknown"])
        self.assertEqual(records2[0]["name"], "")

    def test_infer_types_false_keeps_strings(self):
        csv_text = "id,score,active\n1,8.4,true\n"
        records = read_csv(csv_text, infer_types=False)
        self.assertEqual(records[0], {"id": "1", "score": "8.4", "active": "true"})

    def test_infer_types_false_still_honors_null_values(self):
        csv_text = "id,note\n1,\n2,N/A\n"
        records = read_csv(csv_text, infer_types=False)
        self.assertIsNone(records[0]["note"])
        self.assertIsNone(records[1]["note"])

    def test_header_false_auto_columns(self):
        csv_text = "1,Alice,8.4\n2,Bob,7.1\n"
        records = read_csv(csv_text, header=False)
        self.assertEqual(records[0], {"col_0": 1, "col_1": "Alice", "col_2": 8.4})
        self.assertEqual(records[1], {"col_0": 2, "col_1": "Bob", "col_2": 7.1})

    def test_quoted_values_with_commas_and_newlines(self):
        csv_text = 'id,bio\n1,"Hello, world"\n2,"line one\nline two"\n'
        records = read_csv(csv_text)
        self.assertEqual(records[0]["bio"], "Hello, world")
        self.assertEqual(records[1]["bio"], "line one\nline two")

    def test_unicode(self):
        csv_text = "id,name\n1,日本語\n2,Ångström\n"
        records = read_csv(csv_text)
        self.assertEqual(records[0]["name"], "日本語")
        self.assertEqual(records[1]["name"], "Ångström")

    def test_nested_unflatten_default(self):
        csv_text = "id,user.name,user.email\n1,Alice,alice@example.com\n"
        records = read_csv(csv_text)
        self.assertEqual(
            records[0],
            {
                "id": 1,
                "user": {"name": "Alice", "email": "alice@example.com"},
            },
        )

    def test_nested_disabled(self):
        csv_text = "id,user.name\n1,Alice\n"
        records = read_csv(csv_text, nested=False)
        self.assertEqual(records[0], {"id": 1, "user.name": "Alice"})

    def test_custom_flatten_sep(self):
        csv_text = "id,user__name\n1,Alice\n"
        records = read_csv(csv_text, flatten_sep="__")
        self.assertEqual(records[0], {"id": 1, "user": {"name": "Alice"}})

    def test_custom_delimiter(self):
        csv_text = "id;name\n1;Alice\n"
        records = read_csv(csv_text, delimiter=";")
        self.assertEqual(records[0], {"id": 1, "name": "Alice"})

    def test_empty_csv(self):
        self.assertEqual(read_csv(""), [])

    def test_reads_from_file_path(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("id,name\n42,Alice\n")
            path = f.name
        try:
            records = read_csv(path)
            self.assertEqual(records[0], {"id": 42, "name": "Alice"})
        finally:
            os.unlink(path)


class TestConvertCsvDispatch(unittest.TestCase):
    def test_convert_csv_path_to_json(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("id,name,active\n1,Alice,true\n2,Bob,false\n")
            path = f.name
        try:
            result = convert(path, "json")
            parsed = json.loads(result.data)
            self.assertEqual(
                parsed,
                [
                    {"id": 1, "name": "Alice", "active": True},
                    {"id": 2, "name": "Bob", "active": False},
                ],
            )
            self.assertEqual(result.format, "json")
            self.assertEqual(result.stats.rows, 2)
        finally:
            os.unlink(path)

    def test_convert_csv_string_with_from_format(self):
        csv_text = "id,name\n1,Alice\n"
        result = convert(csv_text, "json", from_format="csv")
        self.assertEqual(json.loads(result.data), [{"id": 1, "name": "Alice"}])

    def test_convert_csv_to_markdown(self):
        csv_text = "id,name\n1,Alice\n2,Bob\n"
        result = convert(csv_text, "markdown", from_format="csv")
        self.assertIn("Alice", result.data)
        self.assertIn("Bob", result.data)

    def test_round_trip_json_csv_json(self):
        original = [
            {"id": 1, "name": "Alice", "score": 8.4},
            {"id": 2, "name": "Bob", "score": 7.1},
        ]
        csv_converter = JsonToCSV(original)
        csv_converter.converter()
        csv_data = csv_converter.get_converted_data().data
        result = convert(csv_data, "json", from_format="csv")
        self.assertEqual(json.loads(result.data), original)

    def test_round_trip_with_nested(self):
        original = [{"id": 1, "user": {"name": "Alice", "email": "a@example.com"}}]
        csv_converter = JsonToCSV(original)
        csv_converter.converter()
        csv_data = csv_converter.get_converted_data().data
        result = convert(csv_data, "json", from_format="csv")
        self.assertEqual(json.loads(result.data), original)

    def test_explicit_from_format_overrides_extension(self):
        # A .csv file path but the caller forces JSON parsing — should fail
        # because the file isn't JSON.
        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("id,name\n1,Alice\n")
            path = f.name
        try:
            with self.assertRaises((ValueError, json.JSONDecodeError)):
                convert(path, "json", from_format="json")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
