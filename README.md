# Photo View

A simple PySide6-based photo viewer/organizer with a tree view, preview pane, and basic copy/delete actions.

## Requirements
- Python 3.10+
- PySide6
- PyYAML
- exiv2 ([python-exiv2](https://pypi.org/project/exiv2/), for EXIF/preview handling — prebuilt wheels, no manual build)
- Send2Trash

## Quick Start
```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python launch.py
```

All dependencies install as prebuilt wheels — nothing to compile. After an OS
upgrade or on a new machine, just reinstall Python and repeat the steps above.

## Setting Up on a New Machine
1. Install Python 3.10+ (pyenv, Homebrew, or python.org — the macOS built-in
   `/usr/bin/python3` is too old).
2. Copy this folder (or `git clone` it) to the new machine. Do **not** copy the
   `.venv/` directory — virtual environments are not portable.
3. Recreate the environment (see Quick Start above):
   ```sh
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
4. Optionally add the launcher function to `~/.zshrc`:
   ```sh
   photo_view() {
     local repo="$HOME/Documents/devl/photo_view"
     if [ -x "$repo/.venv/bin/python" ]; then
       "$repo/.venv/bin/python" "$repo/launch.py"
     else
       echo "photo_view venv not found. Set it up with:" >&2
       echo "  python3 -m venv $repo/.venv && $repo/.venv/bin/pip install -r $repo/requirements.txt" >&2
       return 1
     fi
   }
   ```
5. On first launch, macOS may ask for permission to access Pictures/Documents/
   removable volumes — allow them, or folder scans will silently come up empty.

### Windows
The app and all dependencies are cross-platform (all install as prebuilt
wheels). Setup differs only in paths:
```bat
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python launch.py
```
Edit `etc/config.yml` to use Windows paths, e.g. `E:/DCIM` for an SD card and
`C:/Users/{username}/Pictures/source` (forward slashes work; `{username}` is
expanded automatically).

## Configuration
Default settings live in `etc/config.yml`:
- `image_root_dirs`: folders scanned for images
- `image_extensions`: file extensions to include (e.g., ARW, JPG)
- `continuous_shoot_threshold_sec`: grouping threshold
- icon and cache size settings

Adjust paths to your machine before running.

## Project Layout
- `photo_view/`: core application code (widgets, model, metadata adapter, config, logging)
- `launch.py`: GUI entry point
- `etc/`: configuration files
- `icons/`: UI assets
- `temp/`: archived scripts/notes not used by the main app

All metadata access goes through `photo_view/metadata.py`, so the underlying
EXIF library can be swapped without touching the rest of the app.

## Notes
This is a GUI app with manual smoke testing; no automated tests are currently configured.

### Historical: py3exiv2 (no longer used)
Earlier versions used py3exiv2, which had to be compiled against Homebrew
exiv2/boost-python with a hand-edited `setup.py`. That dependency has been
replaced by python-exiv2 wheels; the old `py3exiv2/` virtual environment can be
deleted once the new setup is confirmed working.
