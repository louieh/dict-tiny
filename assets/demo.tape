Output demo_2_0_0.gif

# =========================
# Window
# =========================
Set Width 1300
Set Height 1000
Set Padding 44
Set Margin 20
Set MarginFill "#11111b"
Set BorderRadius 24
Set WindowBar Colorful

# =========================
# Font
# =========================
# Set FontFamily "Sarasa Term SC"

Set FontSize 32
Set LineHeight 1.3

# =========================
# Terminal Theme
# =========================
Set Theme { 
    "black": "#45475a", 
    "red": "#f38ba8", 
    "green": "#a6e3a1", 
    "yellow": "#f9e2af", 
    "blue": "#89b4fa", 
    "magenta": "#f5c2e7", 
    "cyan": "#94e2d5", 
    "white": "#bac2de", 
    "brightBlack": "#585b70", 
    "brightRed": "#f38ba8", 
    "brightGreen": "#a6e3a1", 
    "brightYellow": "#f9e2af", 
    "brightBlue": "#89b4fa", 
    "brightMagenta": "#f5c2e7", 
    "brightCyan": "#94e2d5", 
    "brightWhite": "#a6adc8", 
    "background": "#1e1e2e", 
    "foreground": "#cdd6f4", 
    "selection": "#585b70", 
    "cursor": "#f5e0dc" 
}
#Set Theme {
#  "background": "#002b36",
#  "foreground": "#93a1a1",
#
#  "black": "#073642",
#  "red": "#dc322f",
#  "green": "#2aa198",
#  "yellow": "#b58900",
#  "blue": "#268bd2",
#  "magenta": "#d33682",
#  "cyan": "#2aa198",
#  "white": "#eee8d5",
#
#  "brightBlack": "#586e75",
#  "brightRed": "#cb4b16",
#  "brightGreen": "#859900",
#  "brightYellow": "#b58900",
#  "brightBlue": "#268bd2",
#  "brightMagenta": "#d33682",
#  "brightCyan": "#2aa198",
#  "brightWhite": "#fdf6e3",
#
#  "selection": "#0d4f5c",
#  "cursor": "#93a1a1"
#}

# =========================
# Animation
# =========================
Set TypingSpeed 100ms
Set Framerate 60
Set CursorBlink false

# =========================
# Demo
# =========================
Sleep 1s

# Enter interactive mode
Type "dict-tiny -i" 
Sleep 400ms
Enter

Sleep 500ms

# Type partial word
Type "so" Sleep 50ms

# Trigger auto-completion
Tab
Sleep 1s

# Select the 5th suggestion
Down
Sleep 200ms
Down
Sleep 200ms
Down
Sleep 200ms
Down
Sleep 200ms
Down
Sleep 200ms

# Confirm the selected suggestion
Enter
Sleep 1s

# Exit interactive mode
Ctrl+d
Sleep 2s
