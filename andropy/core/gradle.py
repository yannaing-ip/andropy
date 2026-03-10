import subprocess
import platform
import os
from pathlib import Path
from andropy.core.platform import is_termux, get_system_aapt2


def get_gradlew(project_root: Path) -> Path:
    """Get gradlew path inside android project."""
    return project_root / "app" / "gradlew"


def run_gradle(project_root: Path, task: str, no_daemon: bool):
    """Run a Gradle task inside the android project."""
    gradlew = get_gradlew(project_root)

    if not gradlew.exists():
        raise FileNotFoundError("gradlew not found inside app/. Is this a valid Andropy project?")

    if os.access(gradlew, os.X_OK):
        cmd = [str(gradlew), task]
    else:
        cmd = ["gradle", task]

    if no_daemon:
        cmd.append("--no-daemon")

    subprocess.run(cmd, cwd=project_root / "app", check=True)


def generate_gradle_wrapper(android_dir: Path, no_daemon: bool):
    """Generate Gradle wrapper inside android project."""
    gradle_cmd = ["gradle", "wrapper"]
    if no_daemon:
        gradle_cmd.append("--no-daemon")
    subprocess.run(gradle_cmd, cwd=android_dir, check=True)


def generate_gradle_properties(android_dir: Path, console):
    """Generate gradle.properties based on current platform."""
    lines = [
        "android.useAndroidX=true",
        "android.enableJetifier=true",
        "org.gradle.jvm.args=-Xmx2048m",
    ]

    if is_termux():
        aapt2_path = get_system_aapt2()
        if aapt2_path:
            lines.append(f"android.aapt2FromMavenOverride={aapt2_path}")
            console.print(f"[dim]→ Termux detected, using system aapt2: [cyan]{aapt2_path}[/cyan][/dim]")
        else:
            console.print("[yellow]⚠ Termux detected but aapt2 not found in PATH. Build may fail.[/yellow]")
    elif platform.system() == "Linux":
        console.print("[dim]→ Linux detected, using AGP bundled aapt2[/dim]")
    elif platform.system() == "Windows":
        console.print("[dim]→ Windows detected, using AGP bundled aapt2[/dim]")
    elif platform.system() == "Darwin":
        console.print("[dim]→ macOS detected, using AGP bundled aapt2[/dim]")

    props_file = android_dir / "gradle.properties"
    props_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print("[dim]→ gradle.properties generated ✅[/dim]")