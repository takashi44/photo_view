# Photo View

A simple PySide6-based photo viewer/organizer with a tree view, preview pane, and basic copy/delete actions.

## Requirements
- Python 3
- PySide6
- PyYAML

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

## Project Layout
- `photo_view/`: core application code (widgets, model, config, logging)
- `launch.py`: GUI entry point
- `etc/`: configuration files
- `icons/`: UI assets

## Notes
This is a GUI app with manual smoke testing; no automated tests are currently configured.
