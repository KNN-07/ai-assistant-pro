# AI Assistant Pro

A modern Windows desktop application that captures screenshots via global hotkeys, analyzes them with Gemini AI, and automatically pastes solutions.

## Features

- **Global Hotkeys** - Trigger screenshot capture from anywhere
- **Multi-Screenshot Queue** - Capture multiple images and analyze them together
- **Gemini AI Integration** - Powered by Google's latest Gemini models
- **API Key Rotation** - Automatic fallback when quota is exceeded
- **Auto-Paste** - Response automatically pasted at cursor position
- **Modern UI** - Beautiful dark theme with CustomTkinter
- **Floating Widget** - Compact always-on-top capture button
- **System Tray** - Runs silently in background

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Open Settings and add your API key
3. Customize hotkeys and system prompt as needed

## Default Hotkeys

- `Ctrl+Shift+Alt+A` - Capture and analyze
- `Ctrl+Shift+Alt+C` - Queue screenshot (multi-image mode)

## Requirements

- Python 3.10+
- Windows 10/11

## License

MIT
