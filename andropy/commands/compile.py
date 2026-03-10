import typer
from pathlib import Path
from rich.console import Console

from andropy.core.project import find_project_root, read_package_name, find_kt_dir
from andropy.core.sync import sync_folder
from andropy.config import apply_config

app = typer.Typer()
console = Console()


@app.command()
def compile():
    """Compile Python UI files from main/ to XML and KT files."""
    project_root = find_project_root()
    if not project_root:
        console.print("[red]❌ Not inside an Andropy project.[/red]")
        raise typer.Exit()

    main_dir = project_root / "main"
    layout_dir = project_root / "app" / "app" / "src" / "main" / "res" / "layout"

    if not main_dir.exists():
        console.print("[red]❌ main/ folder not found.[/red]")
        raise typer.Exit()

    package_name = read_package_name(project_root)
    kt_dir = find_kt_dir(project_root)
    if not kt_dir:
        console.print("[red]❌ Could not find java source directory.[/red]")
        raise typer.Exit()

    # Sync assets and drawable FIRST
    console.print("\n[bold cyan]🔄 Syncing assets and drawable...[/bold cyan]")
    sync_folder(project_root / "main" / "assets",
                project_root / "app" / "app" / "src" / "main" / "assets", console)
    sync_folder(project_root / "main" / "res" / "drawable",
                project_root / "app" / "app" / "src" / "main" / "res" / "drawable", console)

    # Apply config AFTER sync — so generated drawables don't get deleted
    console.print("\n[bold cyan]📋 Applying config...[/bold cyan]")
    apply_config(project_root)

    # Compile Python UI
    console.print("\n[bold cyan]🎨 Compiling Python UI to XML and Kotlin...[/bold cyan]\n")
    from andropy.compiler import compile_all
    compile_all(main_dir, layout_dir, kt_dir, package_name)
    console.print("\n[bold green]✅ Compilation complete![/bold green]\n")
