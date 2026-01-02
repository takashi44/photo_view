# Repository Guidelines

## Project Structure & Module Organization
- `photo_view/` contains the core PySide6 application (UI widgets, model, config, logging).
- `launch.py` is the main entry point for the GUI application.
- `etc/config.yml` holds default configuration (image roots, extensions, icons, cache sizes).
- `icons/` stores UI assets used in the tree view and preview pane.
- `example_data/` provides sample images for manual testing.
- `py3exiv2/` is a local virtual environment with PySide6/py3exiv2; treat it as vendored tooling.

## Build, Test, and Development Commands
- `python launch.py` starts the photo viewer GUI (requires PySide6 installed).
- `source py3exiv2/bin/activate` then `python launch.py` runs using the bundled virtual environment.
- Utility scripts like `img_fit.py` and `thumb.py` can be executed with `python <script>` after reviewing their intent.

## Coding Style & Naming Conventions
- Use Python with 4-space indentation; follow the spacing patterns already present in `photo_view/` modules.
- Classes use `CamelCase` (e.g., `PV_MainWindow`), functions/variables use `snake_case`.
- Keep Qt signal/slot usage consistent with PySide6 idioms in the existing UI code.

## Testing Guidelines
- No automated test framework is configured.
- Perform a manual smoke test by running `python launch.py` and browsing folders defined in `etc/config.yml`.
- If adding tests, place them under `tests/` and use `test_*.py` naming; document the runner you choose.

## Commit & Pull Request Guidelines
- No Git history is available in this repository; use short, imperative commit subjects (e.g., "Add cache size config").
- PRs should describe behavior changes, list updated config keys, and include screenshots for UI updates.

## Configuration Tips
- `etc/config.yml` uses absolute paths; adjust for your machine and avoid committing local-only path changes unless intended.
