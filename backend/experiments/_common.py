"""Shared helpers for experiment scripts.

Adds the backend root to sys.path so we can `from app.services...` import
without installing the app as a package.
"""
from __future__ import annotations

import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
BACKEND_ROOT = HERE.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

DATASET = HERE / "dataset"
RESULTS = HERE / "results"
PLOTS = HERE / "plots"
RESULTS.mkdir(exist_ok=True)
PLOTS.mkdir(exist_ok=True)


def list_images(extensions=(".png",)) -> list[pathlib.Path]:
    """Return sorted list of dataset images (case-insensitive on extension)."""
    wanted = {e.lower() for e in extensions}
    files = [p for p in DATASET.iterdir()
             if p.is_file() and p.suffix.lower() in wanted]
    if not files:
        raise SystemExit(
            f"No images found in {DATASET}. "
            "See experiments/README.md section 2."
        )
    return sorted(files)


def read_bytes(path: pathlib.Path) -> bytes:
    return path.read_bytes()
