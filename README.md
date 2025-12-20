# JON - Just another notepad

JON is a lightweight, Tkinter-powered notepad built to provide the essentials for quickly editing plain-text files.

## Requirements
- Python 3.10+ (with Tkinter available in your Python installation)
- Windows, macOS, or Linux desktop environment

## Running the app
From the project root, launch the editor with:

```bash
python PyNote.py
```

You can optionally pass a file path to open immediately:

```bash
python PyNote.py path/to/file.txt
```

## Features
- Create, open, save, and “Save As” for plain text files
- Unsaved-change prompts on exit or before opening another file
- Word wrap toggle and font picker
- Find and replace with case-insensitive matching
- Undo, cut/copy/paste, and select-all shortcuts
- Status bar with live line/column indicator plus character/word counts
- Optional startup file loading via command-line argument

## Keyboard shortcuts
- `Ctrl + Z` – Undo
- `Ctrl + X/C/V` – Cut, Copy, Paste
- `Ctrl + F` – Find / Replace
- `Ctrl + A` – Select All

## Notes
- If `pynote_icon.ico` is present in the project directory, it will be used as the window icon (fallback-safe on platforms that do not support `.ico`).
- Build numbers only increase when `IS_BUILD` is set to `True` in `PyNote.py`.
