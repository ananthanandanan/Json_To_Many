"""
Demo: ConversionResult API
Run with: uv run python examples/conversion_result_demo.py
"""

import os
import tempfile

from json_to_many import convert, ConversionResult

DIVIDER = "-" * 50

# ── Sample data ──────────────────────────────────────
USERS = [
    {
        "id": 1,
        "name": "Alice",
        "role": "admin",
        "address": {"city": "New York", "zip": "10001"},
    },
    {
        "id": 2,
        "name": "Bob",
        "role": "user",
        "address": {"city": "Los Angeles", "zip": "90001"},
    },
    {
        "id": 3,
        "name": "Carol",
        "role": "user",
        "address": {"city": "Chicago", "zip": "60601"},
    },
]

CONFIG = {
    "app": "Json2Many",
    "version": "0.2.0",
    "features": {
        "markdown": True,
        "xml": True,
        "csv": True,
    },
}


def section(title):
    print(f"\n{DIVIDER}\n  {title}\n{DIVIDER}")


# ── 1. ConversionResult is always returned ───────────
section("1. convert() always returns ConversionResult")

result = convert(USERS, "csv")

print(f"Type   : {type(result).__name__}")
print(f"Format : {result.format}")
print(f"Rows   : {result.stats.rows}")
print(f"Fields : {result.stats.fields}")
print(f"Data preview:\n{result.data[:120]}...")


# ── 2. Stats across all three formats ────────────────
section("2. Stats — rows and fields per format")

for fmt in ("csv", "xml", "markdown"):
    r = convert(USERS, fmt)
    print(f"  {fmt:<10}  rows={r.stats.rows}  fields={r.stats.fields}")


# ── 3. ConversionResult on a dict (not a list) ───────
section("3. Dict input — rows reflects top-level key count")

result = convert(CONFIG, "markdown")
print(f"Format : {result.format}")
print(f"Rows   : {result.stats.rows}  (top-level keys in CONFIG)")
print(f"Data preview:\n{result.data[:200]}")


# ── 4. .data is always the converted string ──────────
section("4. .data gives the string regardless of output_file")

with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
    tmp = f.name

result = convert(USERS, "csv", output_file=tmp)
print(f"File written : {tmp}")
print(f"result.data still accessible: {len(result.data)} chars")
os.unlink(tmp)


# ── 5. Warnings list (plumbed, ready for options) ────
section("5. stats.warnings — empty now, populated by options in next chunks")

result = convert(USERS, "csv")
print(f"Warnings: {result.stats.warnings!r}")
print("  (will surface things like missing fields or skipped columns once")
print("   CSV/XML options are added in chunks 1.2 and 1.3)")


# ── 6. Type check in your own code ───────────────────
section("6. isinstance check — safe to use in typed code")

result = convert(CONFIG, "xml")
assert isinstance(result, ConversionResult), "always a ConversionResult"
print("isinstance(result, ConversionResult) → True")
print(f"XML snippet: {result.data[:80]}...")

print(f"\n{DIVIDER}\nAll demos complete.\n")
