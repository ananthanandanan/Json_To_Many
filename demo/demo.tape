# Output
Output demo/demo.gif

# Terminal settings
Set Shell "zsh"
Set FontSize 14
Set Width 900
Set Height 500
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 60ms

# Activate the venv so json2many is on PATH
Hide
Type "source .venv/bin/activate && cd demo"
Enter
Sleep 500ms
Show

# --- Step 1: inspect the file ---
Sleep 500ms
Type "json2many schema users.json"
Enter
Sleep 2s

# --- Step 2: convert to multiple formats ---
Sleep 800ms
Type "json2many convert users.json --to csv --to markdown --to html --output-dir ./dist/"
Enter
Sleep 2s

# --- Step 3: peek at the CSV output ---
Sleep 800ms
Type "cat dist/users.csv"
Enter
Sleep 2s

Sleep 1s
