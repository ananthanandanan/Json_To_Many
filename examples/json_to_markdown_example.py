#!/usr/bin/env python3
"""Run examples demonstrating json_to_many Markdown options."""

from json_to_many import convert

# Example 1: Basic conversion with title + bullet lists
print("=" * 60)
print("Example 1: Basic with title and bullet lists")
print("=" * 60)
data1 = {
    "Project": {
        "Name": "MyApp",
        "Tech": ["Python", "FastAPI"],
        "Version": "1.0",
    }
}
out1 = convert(data1, "markdown", return_data=True, title="Project Report")
print(out1)

# Example 2: Table for list-of-dicts (API-style data)
print("\n" + "=" * 60)
print("Example 2: Table for list of dicts (table_for_lists=True)")
print("=" * 60)
data2 = {
    "Users": [
        {"name": "Alice", "role": "admin", "email": "alice@example.com"},
        {"name": "Bob", "role": "user", "email": "bob@example.com"},
        {"name": "Carol", "role": "user", "email": "carol@example.com"},
    ]
}
out2 = convert(data2, "markdown", return_data=True, table_for_lists=True)
print(out2)

# Example 3: Frontmatter (for static site generators)
print("\n" + "=" * 60)
print("Example 3: With frontmatter")
print("=" * 60)
data3 = {"Summary": "API Changelog for v2.1", "Breaking": False}
out3 = convert(
    data3,
    "markdown",
    return_data=True,
    frontmatter={
        "title": "API Changelog",
        "date": "2025-02-21",
        "version": "2.1",
        "draft": False,
    },
    title="API Reference",
)
print(out3)

# Example 4: Code blocks for API docs
print("\n" + "=" * 60)
print("Example 4: Code block keys (API request/response)")
print("=" * 60)
data4 = {
    "endpoint": "/users",
    "method": "GET",
    "example_request": '{"filter": "active", "limit": 10}',
    "example_response": '{"data": [{"id": 1, "name": "Alice"}], "total": 1}',
}
out4 = convert(
    data4,
    "markdown",
    return_data=True,
    code_block_keys=["example_request", "example_response"],
    title="GET /users",
)
print(out4)

# Example 5: Combined - all options
print("\n" + "=" * 60)
print("Example 5: Combined (heading_offset, max_heading_level, etc.)")
print("=" * 60)
data5 = {
    "Users": [
        {"name": "Alice", "role": "admin"},
        {"name": "Bob", "role": "user"},
    ],
    "Config": {"timeout": 30, "retries": [1, 2, 3]},
}
out5 = convert(
    data5,
    "markdown",
    return_data=True,
    title="Embedded Report",
    heading_offset=1,
    max_heading_level=4,
    bullet_lists=True,
    table_for_lists=True,
    frontmatter={"doc": "example", "generated": True},
)
print(out5)
