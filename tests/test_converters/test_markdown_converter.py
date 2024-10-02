# tests/test_converters/test_markdown_converter.py
import unittest
from json_to_many.converters.markdown_converter import JsonToMarkdown


class TestJsonToMarkdown(unittest.TestCase):
    def test_conversion(self):
        data = {"title": "Test", "content": "This is a test."}
        converter = JsonToMarkdown(data)
        converter.convert()
        expected_output = "# title\n\nTest\n\n# content\n\nThis is a test.\n\n"
        self.assertEqual(converter.get_converted_data(), expected_output)


if __name__ == "__main__":
    unittest.main()
