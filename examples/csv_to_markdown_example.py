"""CSV → Markdown report.

Showcases the round-trip pitch: once the CSV is parsed into typed Python
records, every existing output converter (markdown, html, sql, ...) works
unchanged.
"""

from pathlib import Path

from json_to_many import convert

csv_path = Path(__file__).parent / "users.csv"

# Same source CSV — three different output formats, one pipeline.
md = convert(csv_path, "markdown", title="User export", table_for_lists=True)
print("--- markdown ---")
print(md.data)

html = convert(csv_path, "html", title="User export", table_style="github")
print("\n--- html (first 200 chars) ---")
print(html.data[:200], "...")

sql = convert(csv_path, "sql", table="users", include_create=True)
print("\n--- sql ---")
print(sql.data)
