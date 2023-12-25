from __future__ import annotations

from paved_path import PavedPath

from ActualExclusives.settings import BASE_DIR as _BASE_DIR

# Convert BASE_DIR to an PavedPath object to make it easier to work with
BASE_DIR = PavedPath(_BASE_DIR)

DOWNLOADED_FILES_DIR = BASE_DIR / "downloaded_files"
