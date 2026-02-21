import unittest
from json_to_many.converters.markdown_converter import JsonToMarkdown


class TestJsonToMarkdown(unittest.TestCase):
    def test_conversion(self):
        data = {"title": "Test", "content": "This is a test."}
        converter = JsonToMarkdown(data)
        converter.converter()
        expected_output = "# title\n\nTest\n\n# content\n\nThis is a test.\n\n"
        self.assertEqual(converter.get_converted_data(), expected_output)

    def test_heading_offset(self):
        data = {"Project": {"Name": "MyApp"}}
        converter = JsonToMarkdown(data, heading_offset=1)
        converter.converter()
        expected = "## Project\n\n### Name\n\nMyApp\n\n"
        self.assertEqual(converter.get_converted_data(), expected)

    def test_max_heading_level(self):
        data = {"A": {"B": {"C": {"D": {"E": {"F": {"G": "deep"}}}}}}}
        converter = JsonToMarkdown(data, max_heading_level=3)
        converter.converter()
        self.assertIn("### C\n\n", converter.get_converted_data())
        self.assertIn("**D**\n\n", converter.get_converted_data())
        self.assertIn("**E**\n\n", converter.get_converted_data())

    def test_bullet_lists_true(self):
        data = {"Tech": ["Python", "FastAPI"]}
        converter = JsonToMarkdown(data, bullet_lists=True)
        converter.converter()
        expected = "# Tech\n\n- Python\n- FastAPI\n\n"
        self.assertEqual(converter.get_converted_data(), expected)

    def test_bullet_lists_false(self):
        data = {"Tech": ["Python", "FastAPI"]}
        converter = JsonToMarkdown(data, bullet_lists=False)
        converter.converter()
        expected = "# Tech\n\nPython\n\nFastAPI\n\n"
        self.assertEqual(converter.get_converted_data(), expected)

    def test_title(self):
        data = {"Author": "Jane"}
        converter = JsonToMarkdown(data, title="API Reference")
        converter.converter()
        expected = "# API Reference\n\n# Author\n\nJane\n\n"
        self.assertEqual(converter.get_converted_data(), expected)


if __name__ == "__main__":
    unittest.main()
