import json
from pathlib import Path


def load_last_config(project_root: Path) -> dict:
    """Load previously saved config state."""
    state_file = project_root / ".andropy" / "last_config.json"
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding="utf-8"))


def save_config_state(project_root: Path, config: dict):
    """Save current config state for future comparison."""
    andropy_dir = project_root / ".andropy"
    andropy_dir.mkdir(exist_ok=True)
    state_file = andropy_dir / "last_config.json"
    state_file.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_changes(current: dict, previous: dict) -> set:
    """Return set of keys that changed."""
    if not previous:
        return set(current.keys())
    return {key for key in current if current.get(key) != previous.get(key)}