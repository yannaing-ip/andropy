import typer
from rich.console import Console
from andropy.core.project import find_project_root
from andropy.core.gradle import run_gradle

app = typer.Typer()
console = Console()


@app.command()
def build(
    no_daemon: bool = typer.Option(False, "--no-daemon", help="Run Gradle without daemon"),
    release: bool = typer.Option(False, "--release", help="Build release APK")
):
    """Build the Android project into an APK."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]❌ Not inside an Andropy project.[/red]")
        raise typer.Exit()

    task = "assembleRelease" if release else "assembleDebug"
    build_type = "release" if release else "debug"

    console.print(f"\n[bold green]🔨 Building {build_type} APK...[/bold green]\n")
    try:
        run_gradle(project_root, task, no_daemon)
        apk_path = project_root / "app" / "app" / "build" / "outputs" / "apk" / build_type / f"app-{build_type}.apk"
        console.print(f"\n[bold green]✅ Build successful![/bold green]")
        console.print(f"[dim]→ APK: [cyan]{apk_path}[/cyan][/dim]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Build failed: {e}[/red]\n")
        raise typer.Exit()