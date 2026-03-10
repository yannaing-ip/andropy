import os
from pathlib import Path


def find_project_root() -> Path | None:
    """Walk up directories to find an Andropy project root."""
    current = Path.cwd()
    for path in [current, *current.parents]:
        if (path / "manage.py").exists() and \
           (path / "config.py").exists() and \
           (path / "app").exists() and \
           (path / "main").exists():
            return path
    return None


def read_package_name(project_root: Path) -> str:
    """Read package name from app/app/build.gradle.kts."""
    build_gradle = project_root / "app" / "app" / "build.gradle.kts"
    if build_gradle.exists():
        for line in build_gradle.read_text().splitlines():
            if "applicationId" in line:
                return line.split('"')[1]
    return "com.example.app"


def find_kt_dir(project_root: Path) -> Path | None:
    """Find the java/kotlin source directory."""
    java_base = project_root / "app" / "app" / "src" / "main" / "java"
    if java_base.exists():
        for path in java_base.rglob("*"):
            if path.is_dir() and not any(p.is_dir() for p in path.iterdir()):
                return path
        return java_base
    return None


def create_project_structure(project_dir: Path, main_dir: Path, android_dir: Path, console):
    """Create all required project folders."""
    (main_dir / "assets" / "fonts").mkdir(parents=True, exist_ok=True)
    (main_dir / "res" / "drawable").mkdir(parents=True, exist_ok=True)
    (android_dir / "app" / "src" / "main" / "assets").mkdir(parents=True, exist_ok=True)
    (android_dir / "app" / "src" / "main" / "res" / "drawable").mkdir(parents=True, exist_ok=True)
    console.print("[dim]→ Project folders created ✅[/dim]")


def replace_placeholders(content: str, app_name: str, package_name: str) -> str:
    """Replace template placeholders."""
    package_path = package_name.replace(".", "/")
    return (content
            .replace("{{app_name}}", app_name)
            .replace("{{package_name}}", package_name)
            .replace("{{package_path}}", package_path))