import importlib.util
import sys
import types
from pathlib import Path
from andropy.ui.activity import ActivityUI, ActivityLogic


def parse_activity_file(python_file: Path) -> dict:
    """
    Read a Python activity file and classify all classes.

    Returns:
    {
        "ui":     <ActivityUI subclass> or None,
        "logic":  <ActivityLogic subclass> or None,
        "normal": [<other classes>]
    }
    """
    module = _load_module(python_file)

    result = {
        "ui":     None,
        "logic":  None,
        "normal": []
    }

    for name in dir(module):
        obj = getattr(module, name)

        if not isinstance(obj, type):
            continue

        # Skip imported base classes
        if obj in (ActivityUI, ActivityLogic):
            continue

        if issubclass(obj, ActivityUI):
            result["ui"] = obj
        elif issubclass(obj, ActivityLogic):
            result["logic"] = obj
        else:
            if getattr(obj, "__module__", "") == module.__name__:
                result["normal"].append(obj)

    return result


def _load_module(python_file: Path):
    """Load a Python activity file as a module."""
    dummy_main = types.ModuleType("main")
    sys.modules["main"] = dummy_main

    try:
        spec = importlib.util.spec_from_file_location("activity_module", python_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop("main", None)

    return module