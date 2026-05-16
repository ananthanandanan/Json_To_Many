"""CSV → JSON with type inference and nested unflattening.

Reads `users.csv` (sitting next to this script) and emits typed, nested JSON.
The `address.city` / `address.country` dotted columns round-trip back into a
nested `address` object thanks to the symmetric `flatten_sep`.
"""

from pathlib import Path

from json_to_many import convert

csv_path = Path(__file__).parent / "users.csv"

# 1. Default: extension dispatch + type inference + nested unflatten
result = convert(csv_path, "json", indent=2)
print("--- typed + nested JSON ---")
print(result.data)
print(f"stats: {result.stats.rows} rows, {result.stats.fields} fields\n")

# 2. Disable type inference — every value stays a string
flat_strings = convert(csv_path, "json", infer_types=False, indent=2)
print("--- infer_types=False (strings only, but null_values still apply) ---")
print(flat_strings.data[:200], "...\n")

# 3. Disable nested unflatten — dotted keys stay flat
flat_keys = convert(csv_path, "json", nested=False, indent=2)
print("--- nested=False (dotted keys preserved) ---")
print(flat_keys.data[:200], "...\n")

# 4. Custom null tokens — treat "GB" as null just to demonstrate the knob
custom_nulls = convert(csv_path, "json", null_values=["", "GB"], indent=2)
print('--- null_values=["", "GB"] ---')
print(custom_nulls.data[:300], "...\n")

# 5. CSV string in memory (no file path) — use from_format
csv_string = "id,name,active\n1,Alice,true\n2,Bob,false\n"
in_memory = convert(csv_string, "json", from_format="csv")
print("--- in-memory CSV string ---")
print(in_memory.data)

# 6. header=False — first row becomes data; columns auto-named col_0, col_1, ...
no_header = convert(csv_path, "json", header=False, indent=2)
print("--- header=False (header row parsed as data, cols become col_N) ---")
print(no_header.data[:400], "...\n")
