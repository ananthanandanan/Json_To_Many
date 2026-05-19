from __future__ import annotations

import json
import os
import tempfile
import unittest
import warnings

from json_to_many import convert
from json_to_many.readers.jsonl_reader import read_jsonl


class TestJsonlReader(unittest.TestCase):
    def test_well_formed(self):
        text = '{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n'
        records = read_jsonl(text)
        self.assertEqual(
            records,
            [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
        )

    def test_types_preserved(self):
        # JSON values carry their types — no inference needed.
        text = '{"id": 1, "score": 8.4, "active": true, "tag": null}\n'
        records = read_jsonl(text)
        self.assertEqual(
            records[0],
            {"id": 1, "score": 8.4, "active": True, "tag": None},
        )

    def test_blank_lines_tolerated(self):
        text = '\n{"id": 1}\n\n   \n{"id": 2}\n'
        records = read_jsonl(text)
        self.assertEqual(records, [{"id": 1}, {"id": 2}])

    def test_trailing_newline(self):
        text = '{"id": 1}\n{"id": 2}\n'
        self.assertEqual(read_jsonl(text), [{"id": 1}, {"id": 2}])

    def test_no_trailing_newline(self):
        text = '{"id": 1}\n{"id": 2}'
        self.assertEqual(read_jsonl(text), [{"id": 1}, {"id": 2}])

    def test_bad_line_warns_non_strict(self):
        text = '{"id": 1}\nnot json\n{"id": 3}\n'
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            records = read_jsonl(text)
        self.assertEqual(records, [{"id": 1}, {"id": 3}])
        self.assertEqual(len(caught), 1)
        self.assertIn("line 2", str(caught[0].message))

    def test_bad_line_raises_strict(self):
        text = '{"id": 1}\nnot json\n'
        with self.assertRaises(ValueError) as ctx:
            read_jsonl(text, strict=True)
        self.assertIn("line 2", str(ctx.exception))

    def test_empty(self):
        self.assertEqual(read_jsonl(""), [])
        self.assertEqual(read_jsonl("\n\n   \n"), [])

    def test_reads_from_file_path(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            f.write('{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n')
            path = f.name
        try:
            records = read_jsonl(path)
            self.assertEqual(records[0], {"id": 1, "name": "Alice"})
            self.assertEqual(records[1], {"id": 2, "name": "Bob"})
        finally:
            os.unlink(path)

    def test_unicode(self):
        text = '{"name": "日本語"}\n{"name": "Ångström"}\n'
        records = read_jsonl(text)
        self.assertEqual(records[0]["name"], "日本語")
        self.assertEqual(records[1]["name"], "Ångström")

    def test_nested_objects(self):
        text = '{"id": 1, "user": {"name": "Alice", "email": "a@example.com"}}\n'
        records = read_jsonl(text)
        self.assertEqual(
            records[0],
            {"id": 1, "user": {"name": "Alice", "email": "a@example.com"}},
        )


class TestConvertJsonlDispatch(unittest.TestCase):
    def test_convert_jsonl_path_to_json(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False, encoding="utf-8"
        ) as f:
            f.write('{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n')
            path = f.name
        try:
            result = convert(path, "json")
            self.assertEqual(
                json.loads(result.data),
                [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"},
                ],
            )
            self.assertEqual(result.stats.rows, 2)
        finally:
            os.unlink(path)

    def test_convert_jsonl_string_with_from_format(self):
        text = '{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n'
        result = convert(text, "csv", from_format="jsonl")
        self.assertIn("Alice", result.data)
        self.assertIn("Bob", result.data)

    def test_convert_jsonl_to_markdown(self):
        text = '{"id": 1, "name": "Alice"}\n{"id": 2, "name": "Bob"}\n'
        result = convert(text, "markdown", from_format="jsonl")
        self.assertIn("Alice", result.data)
        self.assertIn("Bob", result.data)

    def test_round_trip_json_jsonl_json(self):
        original = [
            {"id": 1, "name": "Alice", "score": 8.4},
            {"id": 2, "name": "Bob", "score": 7.1},
        ]
        jsonl_result = convert(original, "jsonl")
        roundtripped = convert(jsonl_result.data, "json", from_format="jsonl")
        self.assertEqual(json.loads(roundtripped.data), original)

    def test_strict_propagates_through_convert(self):
        text = '{"id": 1}\nnot json\n'
        with self.assertRaises(Exception):
            convert(text, "json", from_format="jsonl", strict=True)

    def test_non_strict_default_skips_bad_line(self):
        text = '{"id": 1}\nnot json\n{"id": 3}\n'
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = convert(text, "json", from_format="jsonl")
        self.assertEqual(json.loads(result.data), [{"id": 1}, {"id": 3}])


if __name__ == "__main__":
    unittest.main()
