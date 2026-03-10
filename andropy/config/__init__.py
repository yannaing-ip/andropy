from andropy.config.reader import load_config
from andropy.config.tracker import load_last_config, save_config_state, get_changes
from andropy.config.writer import (
    update_strings_xml,
    update_styles_xml,
    update_build_gradle,
    update_manifest,
    sync_activity_files,
)
from pathlib import Path


def apply_config(project_root: Path):
    """Read config.py, detect changes, apply only what changed."""
    print("\n  📋 Reading config.py...")
    current = load_config(project_root)
    previous = load_last_config(project_root)
    changes = get_changes(current, previous)

    if not changes:
        print("  ✅ No config changes detected.")
    else:
        print(f"  🔍 Changes detected: {', '.join(changes)}\n")

        if "APP_NAME" in changes:
            update_strings_xml(project_root, current)

        if "VERSION_CODE" in changes or "VERSION_NAME" in changes:
            update_build_gradle(project_root, current)

    # Always regenerate styles and drawables — drawables may have been deleted by sync
    update_styles_xml(project_root, current)

    # Generate launcher icon
    from andropy.config.writer import generate_launcher_icon
    generate_launcher_icon(project_root, current)

    # Always regenerate manifest
    update_manifest(project_root, current)

    # Always sync activity files
    print("\n  🔄 Syncing activity files...")
    sync_activity_files(project_root)

    save_config_state(project_root, current)
    print("\n  ✅ Config applied!")
    return current