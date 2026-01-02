# Photo View

A simple PySide6-based photo viewer/organizer with a tree view, preview pane, and basic copy/delete actions.

## Requirements
- Python 3
- PySide6
- PyYAML
- py3exiv2 (for EXIF/preview handling)

The repo includes a local virtual environment at `py3exiv2/` that you can activate instead of installing dependencies globally.

## Quick Start
```sh
# Option A: use the bundled virtual environment
source py3exiv2/bin/activate
python launch.py

# Option B: use your system Python (ensure deps installed)
python launch.py
```

## Configuration
Default settings live in `etc/config.yml`:
- `image_root_dirs`: folders scanned for images
- `image_extensions`: file extensions to include (e.g., ARW, JPG)
- `continuous_shoot_threshold_sec`: grouping threshold
- icon and cache size settings

Adjust paths to your machine before running.

## Building py3exiv2 (macOS/Homebrew)
If you need to rebuild `py3exiv2`, the notes below match the local setup used for this repo:
1) `brew install boost-python3 exiv2`
2) Download the source package from https://pypi.org/project/py3exiv2/ and extract it.
3) Edit `setup.py` to add Homebrew include/library paths, for example:
   - `include_dirs=['/opt/homebrew/Cellar/exiv2/0.28.7/include','/opt/homebrew/opt/libssh/include/','/opt/homebrew/Cellar/boost/1.90.0/include/']`
   - `library_dirs=['/opt/homebrew/Cellar/boost-python3/1.90.0/lib','/opt/homebrew/Cellar/exiv2/0.28.7/lib']`
4) Repack the source (`tar -czvf py3exiv2-0.12.0-edited.tar.gz py3exiv2-0.12.0/*`).
5) Build/install in a system Python venv:
   - `pyenv shell system`
   - `python3 -m venv photo_view/myenv`
   - `source photo_view/myenv/bin/activate`
   - `pip install py3exiv2-0.12.0-edited.tar.gz`

## Project Layout
- `photo_view/`: core application code (widgets, model, config, logging)
- `launch.py`: GUI entry point
- `etc/`: configuration files
- `icons/`: UI assets
- `temp/`: archived scripts/notes not used by the main app

## Notes
This is a GUI app with manual smoke testing; no automated tests are currently configured.
