# AGENTS.md

## Cursor Cloud specific instructions

This is a single-file Python Tetris game built with Pygame.

### Project structure

- `tetris.py` — The entire application (single file, ~288 lines)
- `requirements.txt` — Single dependency: `pygame>=2.5.0`

### Running the application

```bash
source venv/bin/activate
DISPLAY=:1 python tetris.py
```

The game requires a graphical display. The Cloud VM has DISPLAY=:1 available via the X11 socket at `/tmp/.X11-unix/X1`.

### Linting

No dedicated linter is configured in the repo. Use `pyflakes` (installed in venv) for basic checks:

```bash
source venv/bin/activate
python -m pyflakes tetris.py
```

### Notes

- ALSA audio warnings on startup are harmless — the game does not use sound.
- The committed `venv/` directory was originally created on macOS with Python 3.9.6 and is replaced during setup with a Linux-compatible Python 3.12 venv.
- There are no automated tests in this repository.
