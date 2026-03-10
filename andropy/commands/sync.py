import typer
from rich.console import Console
from andropy.core.project import find_project_root
from andropy.core.sync import sync_folder

app = typer.Typer()
console = Console()


@app.command()
def sync():
    """Sync assets and drawable from main/ to Android project."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]❌ Not inside an Andropy project.[/red]")
        raise typer.Exit()

    console.print("\n[bold cyan]🔄 Syncing assets and drawable...[/bold cyan]\n")
    sync_folder(project_root / "main" / "assets",
                project_root / "app" / "app" / "src" / "main" / "assets", console)
    sync_folder(project_root / "main" / "res" / "drawable",
                project_root / "app" / "app" / "src" / "main" / "res" / "drawable", console)
    console.print("\n[bold green]✅ Sync complete![/bold green]\n")