import shutil
from pathlib import Path


def is_termux() -> bool:
    """Detect if running inside Termux."""
    return "com.termux" in str(Path.home())


def get_system_aapt2() -> str | None:
    """Find system aapt2 path."""
    return shutil.which("aapt2")