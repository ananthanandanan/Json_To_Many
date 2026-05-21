# Output
Output demo/v0.5.gif

# Terminal settings
Set Shell "zsh"
Set FontSize 14
Set Width 900
Set Height 560
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 60ms

# Activate the venv so json2many is on PATH
Hide
Type "source .venv/bin/activate && cd demo && rm -f users.csv roundtrip.json"
Enter
Sleep 500ms
Show

# --- Beat 1: original JSON has real types ---
Sleep 500ms
Type "cat users.json"
Enter
Sleep 2s

# --- Beat 2: forward — JSON → CSV (types get flattened to text) ---
Sleep 800ms
Type "json2many convert users.json --to csv --output users.csv && cat users.csv"
Enter
Sleep 2s

# --- Beat 3: round-trip — CSV → JSON with real types restored ---
Sleep 800ms
Type "json2many convert users.csv --to json --output roundtrip.json && cat roundtrip.json"
Enter
Sleep 3s

# --- Beat 4: pipe a CSV straight into a typed SQL schema ---
Sleep 800ms
Type "cat users.csv | json2many convert --from csv --to sql --table users --include-create"
Enter
Sleep 3s

Sleep 1s
