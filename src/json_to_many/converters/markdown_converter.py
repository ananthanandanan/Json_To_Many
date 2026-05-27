from typing import Any
from .base_converter import BaseConverter
from ..utils.constants import DEFAULT_ENCODING
from ..result import ConversionResult, ConversionStats


class JsonToMarkdown(BaseConverter):
    def __init__(self, data: dict | list, **options: Any) -> None:
        super().__init__(data, **options)
        self.markdown_lines: list[str] = []
        self.converted_data: str | None = None

    def converter(self) -> None:
        template = self.options.get("template")
        if template:
            from ..templates import get_template

            renderer = get_template(template)(self.data, **self.options)
            self.converted_data = renderer.render()
            # save_to_file() writes markdown_lines; keep it in sync with data.
            self.markdown_lines = [self.converted_data]
            self._stats = ConversionStats(rows=renderer.endpoint_count)
            return
        frontmatter = self.options.get("frontmatter")
        if frontmatter is not None:
            self._emit_frontmatter(frontmatter)
        title = self.options.get("title")
        if title is not None:
            self.markdown_lines.append(f"# {title}\n\n")
        self.parse_elements(self.data, 1)
        self.converted_data = "".join(self.markdown_lines)
        rows = len(self.data) if isinstance(self.data, list) else len(self.data)
        self._stats = ConversionStats(rows=rows)

    def _emit_frontmatter(self, fm):
        """Emit YAML frontmatter block for simple key:value pairs (no PyYAML needed)."""
        self.markdown_lines.append("---\n")
        for key, value in fm.items():
            if isinstance(value, bool):
                val_str = "true" if value else "false"
            elif value is None:
                val_str = "null"
            elif isinstance(value, (str, int, float)):
                val_str = str(value)
                if isinstance(value, str) and (
                    ":" in val_str
                    or "#" in val_str
                    or "\n" in val_str
                    or '"' in val_str
                ):
                    val_str = val_str.replace("\\", "\\\\").replace('"', '\\"')
                    val_str = f'"{val_str}"'
            else:
                continue
            self.markdown_lines.append(f"{key}: {val_str}\n")
        self.markdown_lines.append("---\n\n")

    def parse_elements(self, element, level, parent_key=None):
        if isinstance(element, dict):
            for key, value in element.items():
                self.add_heading(key, level)
                self.parse_elements(value, level + 1, parent_key=key)
        elif isinstance(element, list):
            if self._is_list_of_primitives(element):
                self.add_primitive_list(element)
            elif self._is_list_of_dicts_with_common_keys(element) and self.options.get(
                "table_for_lists", False
            ):
                self.add_table(element, level, parent_key)
            else:
                for item in element:
                    self.parse_elements(item, level)
        else:
            self._add_value(element, parent_key)

    def _is_list_of_primitives(self, lst):
        return len(lst) > 0 and all(not isinstance(x, (dict, list)) for x in lst)

    def _is_list_of_dicts_with_common_keys(self, lst):
        if len(lst) == 0 or not all(isinstance(x, dict) for x in lst):
            return False
        common = set(lst[0].keys())
        for item in lst[1:]:
            common &= set(item.keys())
        return len(common) >= 1

    def _add_value(self, value, key=None):
        code_block_keys = self.options.get("code_block_keys") or []
        if key is not None and key in code_block_keys:
            self.add_code_block(str(value), key)
        else:
            self.add_text(value)

    def add_table(self, items, level, parent_key):
        """Emit a GFM pipe table for a list of dicts with common keys."""
        all_keys = []
        seen = set()
        for item in items:
            for k in item.keys():
                if k not in seen:
                    seen.add(k)
                    all_keys.append(k)
        header = "| " + " | ".join(all_keys) + " |"
        sep = "| " + " | ".join("---" for _ in all_keys) + " |"
        self.markdown_lines.append(header + "\n")
        self.markdown_lines.append(sep + "\n")
        for item in items:
            row = "| " + " | ".join(str(item.get(k, "")) for k in all_keys) + " |"
            self.markdown_lines.append(row + "\n")
        self.markdown_lines.append("\n")

    def add_code_block(self, content, language_hint):
        """Emit a fenced code block with the key name as language hint."""
        self.markdown_lines.append(f"```{language_hint}\n")
        self.markdown_lines.append(content)
        if not content.endswith("\n"):
            self.markdown_lines.append("\n")
        self.markdown_lines.append("```\n\n")

    def add_heading(self, text, level):
        offset = self.options.get("heading_offset", 0)
        max_level = self.options.get("max_heading_level", 6)
        effective_level = max(1, level + offset)
        if effective_level <= max_level:
            self.markdown_lines.append(f"{'#' * effective_level} {text}\n\n")
        else:
            self.markdown_lines.append(f"**{text}**\n\n")

    def add_primitive_list(self, items):
        bullet_lists = self.options.get("bullet_lists", True)
        if bullet_lists:
            for item in items:
                self.markdown_lines.append(f"- {item}\n")
            self.markdown_lines.append("\n")
        else:
            for item in items:
                self.add_text(item)

    def add_text(self, text):
        self.markdown_lines.append(f"{text}\n\n")

    def save_to_file(self, file_name: str) -> None:
        encoding = self.options.get("encoding", DEFAULT_ENCODING)
        with open(file_name, "w", encoding=encoding) as file:
            file.writelines(self.markdown_lines)

    def get_converted_data(self) -> ConversionResult:
        assert self.converted_data is not None
        return ConversionResult(
            data=self.converted_data, format="markdown", stats=self._stats
        )
