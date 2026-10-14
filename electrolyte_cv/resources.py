from __future__ import annotations

import sys
from pathlib import Path


def resource_root() -> Path:
    """Return the directory that contains packaged application resources.

    Source mode: project root (the parent of the ``electrolyte_cv`` package).
    PyInstaller: ``sys._MEIPASS`` when available, which also works for onedir.
    """
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parents[1]


def resource_path(*parts: str) -> Path:
    return resource_root().joinpath(*parts)
