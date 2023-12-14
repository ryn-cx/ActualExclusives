from __future__ import annotations

from extended_path import ExtendedPath

from ActualExclusives.settings import BASE_DIR as _BASE_DIR

# Convert BASE_DIR to an ExtendedPath object to make it easier to work with
BASE_DIR = ExtendedPath(_BASE_DIR)

DOWNLOADED_FILES_DIR = BASE_DIR / "downloaded_files"
