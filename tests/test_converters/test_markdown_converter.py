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

    def test_table_for_lists(self):
        data = {
            "Users": [
                {"name": "Alice", "role": "admin"},
                {"name": "Bob", "role": "user"},
            ]
        }
        converter = JsonToMarkdown(data, table_for_lists=True)
        converter.converter()
        out = converter.get_converted_data()
        self.assertIn("# Users\n\n", out)
        self.assertIn("| name | role |\n", out)
        self.assertIn("| --- | --- |\n", out)
        self.assertIn("| Alice | admin |\n", out)
        self.assertIn("| Bob | user |\n", out)

    def test_table_for_lists_default_false(self):
        data = {"Users": [{"name": "Alice"}, {"name": "Bob"}]}
        converter = JsonToMarkdown(data)
        converter.converter()
        out = converter.get_converted_data()
        self.assertNotIn("| name |", out)
        self.assertIn("# Users\n\n", out)

    def test_frontmatter(self):
        data = {"Author": "Jane"}
        converter = JsonToMarkdown(
            data, frontmatter={"title": "Doc", "version": "1.0", "draft": False}
        )
        converter.converter()
        out = converter.get_converted_data()
        self.assertTrue(out.startswith("---\n"))
        self.assertIn("title: Doc\n", out)
        self.assertIn("version: 1.0\n", out)
        self.assertIn("draft: false\n", out)
        self.assertIn("---\n\n", out)

    def test_code_block_keys(self):
        data = {
            "endpoint": "/users",
            "example_request": '{"filter": "active"}',
        }
        converter = JsonToMarkdown(
            data, code_block_keys=["example_request"]
        )
        converter.converter()
        out = converter.get_converted_data()
        self.assertIn("```example_request\n", out)
        self.assertIn('{"filter": "active"}', out)
        self.assertIn("```\n\n", out)
        self.assertIn("# endpoint\n\n/users\n\n", out)


if __name__ == "__main__":
    unittest.main()
