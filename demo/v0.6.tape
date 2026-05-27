# Output
Output demo/v0.6.gif

# Terminal settings
Set Shell "zsh"
Set FontSize 14
Set Width 900
Set Height 600
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 55ms

# Activate the venv so json2many is on PATH; start on a clean screen
Hide
Type "source .venv/bin/activate && cd demo && rm -rf out && mkdir -p out"
Enter
Sleep 500ms
Type "clear"
Enter
Sleep 300ms
Show

# --- Beat 1: the raw spec is machine-readable, not human-readable ---
Sleep 500ms
Type "head -20 payments.json"
Enter
Sleep 2500ms

# --- Beat 2: one command turns it into clean Markdown API docs ---
Sleep 800ms
Type "json2many convert payments.json --to markdown --template openapi --output out/API.md"
Enter
Sleep 1500ms

# --- Beat 3: the payoff — readable, drop-in API docs ---
Type "head -32 out/API.md"
Enter
Sleep 4s
