import os
import platform
from pathlib import Path


def find_android_sdk() -> str | None:
    """Try to locate Android SDK path."""
    candidates = [
        # Environment variables first
        Path(os.environ.get("ANDROID_HOME", "")),
        Path(os.environ.get("ANDROID_SDK_ROOT", "")),
        # Termux
        Path.home() / "android-sdk",
        # Linux/Mac default
        Path.home() / "Android" / "Sdk",
        # Mac
        Path.home() / "Library" / "Android" / "sdk",
        # Windows
        Path.home() / "AppData" / "Local" / "Android" / "Sdk",
    ]
    for path in candidates:
        if path and str(path) not in ("", "/") and path.exists():
            return str(path)
    return None
