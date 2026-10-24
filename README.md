# MyNotepad (modular version)

## Requirements
- Python 3.10+ (recommended)
- PySide6

## Run
Activate your existing virtual environment, then from this folder run:

```powershell
python main.py
```

If setting up a fresh environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PySide6
python main.py
```

## Project structure

```text
main.py                    # Application entry point
mynotepad/
  __init__.py              # Exposes MyNotepad
  main_window.py           # Window, menus, tabs, file/edit operations
  search_mixin.py          # Find and replace dialog/behavior
  recovery_mixin.py        # Autosave and crash-recovery snapshots
  theme_mixin.py           # Light/dark theme styling and persistence
```

The existing features are kept in separate modules to make future changes easier.
