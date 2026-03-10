import sys
import types
import importlib.util
from pathlib import Path


def load_config(project_root: Path) -> dict:
    """Load and parse config.py from project root."""
    config_file = project_root / "config.py"
    if not config_file.exists():
        raise FileNotFoundError("config.py not found in project root.")

    dummy_main = types.ModuleType("main")
    main_dir = project_root / "main"
    for py_file in main_dir.glob("*.py"):
        setattr(dummy_main, py_file.stem, py_file.stem)

    sys.modules["main"] = dummy_main

    try:
        spec = importlib.util.spec_from_file_location("config", config_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop("main", None)

    return {
        "APP_NAME":              getattr(module, "APP_NAME", "My App"),
        "VERSION_CODE":          getattr(module, "VERSION_CODE", 1),
        "VERSION_NAME":          getattr(module, "VERSION_NAME", "1.0"),
        "THEME":                 getattr(module, "THEME", "light"),
        "LAUNCHER_ICON":         getattr(module, "LAUNCHER_ICON", None),
        "LAUNCHER_ACTIVITY":     getattr(module, "LAUNCHER_ACTIVITY", "main_activity"),
        "COLOR_PRIMARY":         getattr(module, "COLOR_PRIMARY", "#1565C0"),
        "COLOR_PRIMARY_DARK":    getattr(module, "COLOR_PRIMARY_DARK", "#0D47A1"),
        "COLOR_ACCENT":          getattr(module, "COLOR_ACCENT", "#1565C0"),
        "COLOR_BACKGROUND":      getattr(module, "COLOR_BACKGROUND", "#FFFFFF"),
        "COLOR_TEXT_PRIMARY":    getattr(module, "COLOR_TEXT_PRIMARY", "#212121"),
        "COLOR_TEXT_SECONDARY":  getattr(module, "COLOR_TEXT_SECONDARY", "#757575"),
        "COLOR_TEXT_HINT":       getattr(module, "COLOR_TEXT_HINT", "#9E9E9E"),
        "COLOR_DIVIDER":         getattr(module, "COLOR_DIVIDER", "#E0E0E0"),
        "COLOR_INPUT_BG":        getattr(module, "COLOR_INPUT_BG", "#F5F5F5"),
        "COLOR_TOOLBAR_TITLE":   getattr(module, "COLOR_TOOLBAR_TITLE", "#FFFFFF"),
        "COLOR_TOOLBAR_SUB":     getattr(module, "COLOR_TOOLBAR_SUB", "#BBDEFB"),
        "COLOR_BUTTON_TEXT":     getattr(module, "COLOR_BUTTON_TEXT", "#FFFFFF"),
        "BUTTON_RADIUS":         getattr(module, "BUTTON_RADIUS", 4),
    }