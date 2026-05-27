"""Tests for the OpenAPI → Markdown template.

Snapshot tests compare rendered Markdown against committed ``.md`` files under
``__snapshots__/``. To regenerate after an intentional change:

    JSON2MANY_UPDATE_SNAPSHOTS=1 uv run pytest tests/test_templates/test_openapi.py

then review the diff before committing — a changed snapshot is either a real
regression or an intended change.
"""

import json
import os
import unittest
from pathlib import Path

from json_to_many import convert
from json_to_many.exceptions import JsonToManyError
from json_to_many.templates.openapi import OpenApiTemplate

FIXTURES = Path(__file__).parent.parent / "fixtures" / "openapi"
SNAPSHOTS = Path(__file__).parent / "__snapshots__"
UPDATE = os.environ.get("JSON2MANY_UPDATE_SNAPSHOTS") == "1"


def render_fixture(name: str) -> str:
    spec = json.loads((FIXTURES / name).read_text())
    return convert(spec, "markdown", template="openapi").data


class TestOpenApiSnapshots(unittest.TestCase):
    """Render each real spec and compare against its committed snapshot."""

    def _check(self, fixture: str, snapshot: str) -> None:
        rendered = render_fixture(fixture)
        path = SNAPSHOTS / snapshot
        if UPDATE or not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(rendered)
            if not UPDATE:
                self.skipTest(f"created missing snapshot {snapshot}")
            return
        self.assertEqual(
            rendered,
            path.read_text(),
            f"{fixture} output drifted from {snapshot}; rerun with "
            "JSON2MANY_UPDATE_SNAPSHOTS=1 if the change is intended.",
        )

    def test_petstore_30(self):
        self._check("petstore.json", "petstore.md")

    def test_blog_31(self):
        self._check("blog_3_1.json", "blog_3_1.md")

    def test_library_circular(self):
        self._check("library_circular.json", "library_circular.md")


class TestOpenApiBehaviour(unittest.TestCase):
    def test_headline_command_via_convert(self):
        spec = json.loads((FIXTURES / "petstore.json").read_text())
        result = convert(spec, "markdown", template="openapi")
        self.assertTrue(result.data.startswith("# Petstore API"))
        self.assertEqual(result.format, "markdown")
        # Four operations across the fixture.
        self.assertEqual(result.stats.rows, 4)

    def test_endpoints_grouped_by_tag(self):
        out = render_fixture("petstore.json")
        self.assertIn("## Pets\n", out)
        self.assertIn("## Store\n", out)
        # Top-level tag order is honoured: Pets before Store.
        self.assertLess(out.index("## Pets"), out.index("## Store"))

    def test_untagged_operation_under_other_last(self):
        out = render_fixture("blog_3_1.json")
        self.assertIn("## Other\n", out)
        self.assertIn("### GET /health", out)
        # "Other" comes after the real tag section.
        self.assertLess(out.index("## Posts"), out.index("## Other"))

    def test_refs_render_as_links_and_collect(self):
        out = render_fixture("petstore.json")
        self.assertIn("[Pet](#pet)", out)
        self.assertIn("## Schemas", out)
        self.assertIn("### Pet", out)
        # array items ref through the link form
        self.assertIn("array of [Pet](#pet)", out)

    def test_circular_refs_terminate_and_render_once(self):
        out = render_fixture("library_circular.json")
        # Book -> Author -> Book cycle. Each schema heading appears exactly once.
        self.assertEqual(out.count("### Book\n"), 1)
        self.assertEqual(out.count("### Author\n"), 1)

    def test_pipe_escaped_in_table_cells(self):
        out = render_fixture("petstore.json")
        # "Pet status | lifecycle" must not break the table.
        self.assertIn("Pet status \\| lifecycle", out)
        self.assertNotIn("Pet status | lifecycle", out)

    def test_examples_rendered_as_fenced_json(self):
        out = render_fixture("petstore.json")
        self.assertIn("```json", out)
        self.assertIn('"name": "Rex"', out)

    def test_authentication_section(self):
        petstore = render_fixture("petstore.json")
        self.assertIn("## Authentication", petstore)
        self.assertIn("header: X-API-Key", petstore)
        # Per-operation security note.
        self.assertIn("**Security:** apiKey", petstore)

        library = render_fixture("library_circular.json")
        self.assertIn("flows: authorizationCode", library)
        self.assertIn("bearer (JWT)", library)
        self.assertIn("**Security:** oauth2, bearerAuth", library)

    def test_enum_values_surfaced(self):
        out = render_fixture("petstore.json")
        # Enum allowed values appear inline; with a description they are
        # parenthetical, otherwise a standalone "Allowed values:" clause.
        self.assertIn("(allowed values: `available`, `pending`, `sold`)", out)

    def test_oas_31_nullable_and_oneof(self):
        out = render_fixture("blog_3_1.json")
        self.assertIn("string (nullable)", out)  # type: ["string", "null"]
        self.assertIn("integer or number", out)  # oneOf

    def test_invalid_spec_raises(self):
        with self.assertRaises(JsonToManyError):
            convert({"info": {}}, "markdown", template="openapi")

    def test_swagger_2_rejected(self):
        with self.assertRaises(JsonToManyError) as ctx:
            convert({"swagger": "2.0", "info": {}}, "markdown", template="openapi")
        self.assertIn("Swagger 2.0", str(ctx.exception))

    def test_non_dict_input_rejected(self):
        with self.assertRaises(JsonToManyError):
            convert([1, 2, 3], "markdown", template="openapi")

    def test_unknown_template_rejected(self):
        with self.assertRaises(JsonToManyError):
            convert({"openapi": "3.0.0"}, "markdown", template="bogus")

    def test_default_markdown_path_unaffected(self):
        # Without template=, the generic recursive converter still runs.
        out = convert({"title": "Hi", "body": "x"}, "markdown").data
        self.assertEqual(out, "# title\n\nHi\n\n# body\n\nx\n\n")

    def test_output_file_written(self):
        # The template path must populate the file, not just ConversionResult.data.
        import tempfile

        spec = json.loads((FIXTURES / "petstore.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "API.md"
            result = convert(spec, "markdown", template="openapi", output_file=str(out))
            self.assertEqual(out.read_text(), result.data)
            self.assertTrue(out.read_text().startswith("# Petstore API"))

    def test_anchor_slug(self):
        self.assertEqual(OpenApiTemplate._anchor("Pet List"), "pet-list")
        self.assertEqual(OpenApiTemplate._anchor("API_Error!"), "api_error")


if __name__ == "__main__":
    unittest.main()
