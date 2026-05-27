from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path


def resource_path(*parts: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundle_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        direct = bundle_root.joinpath(*parts)
        if direct.exists():
            return direct
        return bundle_root.joinpath("packvision", *parts)
    return Path(__file__).resolve().parents[1].joinpath(*parts)


def app_data_dir() -> Path:
    if getattr(sys, "frozen", False):
        root = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
        return root / "PackVision"
    return Path(__file__).resolve().parents[2] / "data"


def ensure_data_dirs() -> dict[str, Path]:
    root = app_data_dir()
    dirs = {
        "root": root,
        "uploads": root / "uploads",
        "results": root / "results",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def safe_artifact_name(suffix: str) -> str:
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    return f"{uuid.uuid4().hex}{suffix.lower()}"


def write_bytes(directory: Path, suffix: str, content: bytes) -> Path:
    path = directory / safe_artifact_name(suffix)
    path.write_bytes(content)
    return path
