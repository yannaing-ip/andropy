import typer
from rich.console import Console
from andropy.core.project import find_project_root
from andropy.core.gradle import run_gradle

app = typer.Typer()
console = Console()


@app.command()
def clean(
    no_daemon: bool = typer.Option(False, "--no-daemon", help="Run Gradle without daemon")
):
    """Clean the Android build files."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]❌ Not inside an Andropy project.[/red]")
        raise typer.Exit()

    console.print("\n[bold yellow]🧹 Cleaning build files...[/bold yellow]\n")
    try:
        run_gradle(project_root, "clean", no_daemon)
        console.print("\n[bold green]✅ Clean successful![/bold green]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Clean failed: {e}[/red]\n")
        raise typer.Exit()