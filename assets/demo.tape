Output demo.gif
Set FontSize 20
Set Width 800
Set Height 600
Set TypingSpeed 100ms
Set LineHeight 1.4
Set Theme { "name": "Whimsy", "black": "#535178", "red": "#ef6487", "green": "#5eca89", "yellow": "#fdd877", "blue": "#65aef7", "magenta": "#aa7ff0", "cyan": "#43c1be", "white": "#ffffff", "brightBlack": "#535178", "brightRed": "#ef6487", "brightGreen": "#5eca89", "brightYellow": "#fdd877", "brightBlue": "#65aef7", "brightMagenta": "#aa7ff0", "brightCyan": "#43c1be", "brightWhite": "#ffffff", "background": "#29283b", "foreground": "#b3b0d6", "selection": "#3d3c58", "cursor": "#b3b0d6" }
Set Padding 32
Set Margin 16
Set MarginFill "#1e1e2e"
Set BorderRadius 12
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
