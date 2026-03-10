import typer
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from andropy.core.project import find_project_root
from andropy.core.gradle import run_gradle
from andropy.core.platform import is_termux

app = typer.Typer()
console = Console()


@app.command()
def run(
    no_daemon: bool = typer.Option(False, "--no-daemon", help="Run Gradle without daemon")
):
    """Build and install the APK on a connected device."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]❌ Not inside an Andropy project.[/red]")
        raise typer.Exit()

    console.print("\n[bold green]🔨 Building APK...[/bold green]\n")
    try:
        run_gradle(project_root, "assembleDebug", no_daemon)
    except Exception as e:
        console.print(f"\n[red]❌ Build failed: {e}[/red]\n")
        raise typer.Exit()

    apk = project_root / "app" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"

    if is_termux():
        dest = Path("/storage/emulated/0/app-debug.apk")
        shutil.copy(str(apk), dest)
        console.print(f"\n[bold green]✅ APK copied to: [cyan]{dest}[/cyan][/bold green]")
        console.print("[dim]→ Open your file manager and tap the APK to install[/dim]\n")
        subprocess.run(["termux-open", str(dest)], check=False)
    else:
        try:
            run_gradle(project_root, "installDebug", no_daemon)
            console.print("\n[bold green]✅ App installed on device![/bold green]\n")
        except Exception as e:
            console.print(f"\n[red]❌ Install failed: {e}[/red]\n")
            raise typer.Exit()