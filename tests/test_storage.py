import sys
import shutil
import uuid
from pathlib import Path

from packvision.services.storage import resource_path


def test_resource_path_finds_frozen_static_directory(monkeypatch):
    bundle_root = _test_bundle_root()
    static_dir = bundle_root / "static"
    try:
        static_dir.mkdir(parents=True)

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

        assert resource_path("static") == static_dir
    finally:
        shutil.rmtree(bundle_root, ignore_errors=True)


def test_resource_path_supports_legacy_frozen_package_static(monkeypatch):
    bundle_root = _test_bundle_root()
    static_dir = bundle_root / "packvision" / "static"
    try:
        static_dir.mkdir(parents=True)

        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

        assert resource_path("static") == static_dir
    finally:
        shutil.rmtree(bundle_root, ignore_errors=True)


def _test_bundle_root() -> Path:
    return Path.cwd() / ".pytest_cache" / f"bundle-{uuid.uuid4().hex}"
