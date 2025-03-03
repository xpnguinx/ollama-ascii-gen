# Ollama ASCII Art Generator

A feature-rich desktop application that combines ASCII art generation with an Ollama-powered chatbot interface.
<img width="1141" alt="Screenshot 2025-03-01 at 5 25 54 PM" src="https://github.com/user-attachments/assets/99c71718-0452-40b6-9be3-cd70c8eb09ca" />




## Features

### ASCII Art Generator
- Convert text to stylish ASCII art with dozens of font options
- Real-time preview of font selections
- Customizable text and shadow colors with color picker
- Animated shadow effects for a 3D look
- Copy ASCII art to clipboard
- Export as animated GIF
- Multi-line text support 

### Ollama Chat Integration
- Built-in streaming chat interface
- Support for all locally available Ollama models
- Customizable system prompts
- Real-time streaming responses
- Special hacker-themed prompt system
- Special commands: !CODE, !GLITCH, !HACKMODE, !INFOSEC, !DEBUG

## Requirements

- Python 3.6+
- Ollama installed and running locally (for chat features)
- Required Python packages (install via `pip install -r requirements.txt`):
  - tkinter
  - pyfiglet
  - Pillow
  - pyperclip
  - requests

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/penguinlalo/ollama-ascii-gen.git
   cd ollama-ascii-gen
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Usage

### ASCII Art Generation

1. Enter your text in the input field (supports multiple lines)
2. Select a font from the dropdown menu (or use "Preview Font" to see examples)
3. Click "Generate" to create your ASCII art
4. Customize colors using the "ASCII Color" and "Shadow Color" buttons
5. Toggle animation effects on/off as desired
6. Use "Copy to Clipboard" to copy the art for use elsewhere
7. Save as an animated GIF with the "Save as GIF" button

### Using the Ollama Chat

1. Ensure Ollama is running on your local machine
2. Click "Refresh Models" to load available models
3. Select a model from the dropdown
4. Type your message and press Enter or click "Send"
5. Use special commands like !GLITCH or !HACKMODE for specialized responses
6. Customize the system prompt with the "Edit System Prompt" button for different chat behaviors

## Customization

### System Prompt

The default system prompt gives the chatbot a hacker-themed personality. You can modify this by clicking the "Edit System Prompt" button. The prompt uses {Z} as a placeholder for the user's message.

### Color Scheme

The application uses a dark, hacker-inspired theme with customizable ASCII art colors. Modify the color constants at the beginning of the script to change the overall appearance:

```python
# Color palette
BG_BLACK = "#000000"        # Main background
DARK_GRAY = "#111111"       # Secondary background
LIGHT_GRAY = "#CCCCCC"      # Text color
BLUE_PRIMARY = "#3B82F6"    # Default ASCII art color
BLUE_SECONDARY = "#1E40AF"  # Default shadow color
BLUE_HIGHLIGHT = "#60A5FA"  # Highlight blue
```

## Development

This project uses:
- Tkinter for the GUI
- Pyfiglet for ASCII art generation
- Pillow for image manipulation
- Requests for API communication with Ollama

Feel free to fork and enhance with additional features!

## License

MIT

## Creator

Created by @penguinlalo
