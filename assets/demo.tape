Output demo_2_0_0.gif
Set FontFamily "Sarasa Term SC"
Set FontSize 22
Set Width 880
Set Height 600
Set TypingSpeed 100ms
Set LineHeight 1.6
Set Theme { "black": "#45475a", "red": "#f38ba8", "green": "#a6e3a1", "yellow": "#f9e2af", "blue": "#89b4fa", "magenta": "#f5c2e7", "cyan": "#94e2d5", "white": "#bac2de", "brightBlack": "#585b70", "brightRed": "#f38ba8", "brightGreen": "#a6e3a1", "brightYellow": "#f9e2af", "brightBlue": "#89b4fa", "brightMagenta": "#f5c2e7", "brightCyan": "#94e2d5", "brightWhite": "#a6adc8", "background": "#1e1e2e", "foreground": "#cdd6f4", "selection": "#585b70", "cursor": "#f5e0dc" }
Set Padding 40
Set Margin 20
Set MarginFill "#11111b"
Set BorderRadius 16
Set WindowBar Colorful
Set Framerate 30
Set CursorBlink false

Sleep 1s
# Enter interactive mode
Type "dict-tiny -i" Sleep 500ms
Enter
Sleep 2s

# Type partial word
Type "so" Sleep 400ms
Sleep 500ms

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
