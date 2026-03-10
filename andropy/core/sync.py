import shutil
from pathlib import Path


def sync_folder(src: Path, dst: Path, console):
    """Two way sync — copy new files, remove deleted files and folders."""
    if not src.exists():
        if dst.exists():
            shutil.rmtree(dst)
            console.print(f"[dim]  🗑 Removed {dst.name}[/dim]")
        return

    dst.mkdir(parents=True, exist_ok=True)

    # Copy new/updated files and create directories
    for file in src.rglob("*"):
        if file.is_file():
            rel = file.relative_to(src)
            dest = dst / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(file), dest)
            console.print(f"[dim]  → Synced {file.name}[/dim]")
        elif file.is_dir():
            rel = file.relative_to(src)
            (dst / rel).mkdir(parents=True, exist_ok=True)

    # Remove deleted files
    for file in dst.rglob("*"):
        if file.is_file():
            rel = file.relative_to(dst)
            if not (src / rel).exists():
                file.unlink()
                console.print(f"[dim]  🗑 Removed {file.name}[/dim]")

    # Remove empty folders
    for folder in sorted(dst.rglob("*"), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            rel = folder.relative_to(dst)
            if not (src / rel).exists():
                folder.rmdir()
                console.print(f"[dim]  🗑 Removed folder {folder.name}[/dim]")