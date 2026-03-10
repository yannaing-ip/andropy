import typer
import shutil
import subprocess
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

from andropy.core.project import (
    find_project_root,
    create_project_structure,
    replace_placeholders,
)
from andropy.core.sdk import find_android_sdk
from andropy.core.gradle import generate_gradle_wrapper, generate_gradle_properties
from andropy.config import apply_config

app = typer.Typer()
console = Console()


@app.command()
def create(
    app_name: str = typer.Argument(..., help="Name of your app"),
    no_daemon: bool = typer.Option(False, "--no-daemon", help="Run Gradle without daemon")
):
    """Create a new Andropy Android project."""
    project_dir = Path(app_name)

    if project_dir.exists():
        console.print(f"[red]❌ Folder '{app_name}' already exists![/red]")
        raise typer.Exit()

    console.print(f"\n[bold green]🚀 Creating Andropy project: {app_name}[/bold green]\n")

    package_name = Prompt.ask(
        "Enter your Android package name",
        default=f"com.example.{app_name.lower().replace(' ', '').replace('-', '')}",
        show_default=True
    )
    console.print(f"[dim]→ Using package: [cyan]{package_name}[/cyan][/dim]\n")

    main_dir = project_dir / "main"
    android_dir = project_dir / "app"
    main_dir.mkdir(parents=True)
    android_dir.mkdir(parents=True)

    # Copy android template
    template_dir = Path(__file__).parent.parent / "templates" / "android_project"
    shutil.copytree(template_dir, android_dir, dirs_exist_ok=True)

    # Replace placeholders
    for file_path in android_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in (".kt", ".xml", ".kts", ".properties"):
            content = file_path.read_text(encoding="utf-8")
            file_path.write_text(replace_placeholders(content, app_name, package_name), encoding="utf-8")

    # Fix java package folder
    java_base = android_dir / "app" / "src" / "main" / "java"
    placeholder_dir = java_base / "{{package_path}}"
    package_dir = java_base / package_name.replace(".", os.sep)
    package_dir.mkdir(parents=True, exist_ok=True)

    old_kt = placeholder_dir / "MainActivity.kt"
    if old_kt.exists():
        shutil.move(str(old_kt), package_dir / "MainActivity.kt")

    if placeholder_dir.exists():
        try:
            placeholder_dir.rmdir()
            for parent in list(placeholder_dir.parents):
                if parent == java_base:
                    break
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
        except OSError:
            pass

    # Generate local.properties
    sdk_path = find_android_sdk()
    if sdk_path:
        local_props = android_dir / "local.properties"
        local_props.write_text(f"sdk.dir={sdk_path}\n", encoding="utf-8")
        console.print(f"[dim]→ Android SDK found: [cyan]{sdk_path}[/cyan][/dim]")
    else:
        console.print("[yellow]⚠ Could not find Android SDK. Edit app/local.properties manually.[/yellow]")

    # Generate gradle.properties
    generate_gradle_properties(android_dir, console)

    # Generate gradle wrapper
    console.print("[dim]→ Generating Gradle wrapper...[/dim]")
    try:
        generate_gradle_wrapper(android_dir, no_daemon)
        console.print("[dim]→ Gradle wrapper generated ✅[/dim]")
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to generate Gradle wrapper.[/red]")
        raise typer.Exit()
    except FileNotFoundError:
        console.print("[red]❌ Gradle not found. Please install Gradle first.[/red]")
        raise typer.Exit()

    # Generate manage.py
    manage_py = project_dir / "manage.py"
    manage_py.write_text(
        (Path(__file__).parent.parent / "templates" / "manage.py.template").read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    console.print("[dim]→ manage.py generated ✅[/dim]")

    # Generate config.py
    template = Path(__file__).parent.parent / "templates" / "config.py.template"
    content = template.read_text(encoding="utf-8").replace("{{app_name}}", app_name)
    (project_dir / "config.py").write_text(content, encoding="utf-8")
    console.print("[dim]→ config.py generated ✅[/dim]")

    # Create project structure
    create_project_structure(project_dir, main_dir, android_dir, console)

    # Generate main_activity.py
    console.print("[dim]→ Generating main_activity.py...[/dim]")
    main_activity_py = main_dir / "main_activity.py"
    main_activity_py.write_text(
        (Path(__file__).parent.parent / "templates" / "main_activity.py").read_text(encoding="utf-8"),
        encoding="utf-8"
    )
    console.print("[dim]→ main_activity.py generated ✅[/dim]")

    # Auto compile UI
    console.print("[dim]→ Compiling default UI...[/dim]")
    try:
        from andropy.compiler import compile_all
        from andropy.core.project import find_kt_dir
        layout_dir = android_dir / "app" / "src" / "main" / "res" / "layout"
        kt_dir = find_kt_dir(project_dir)
        compile_all(main_dir, layout_dir, kt_dir, package_name)
        console.print("[dim]→ Default UI compiled ✅[/dim]")
    except Exception as e:
        console.print(f"[yellow]⚠ UI compilation failed: {e}[/yellow]")

    console.print(f"\n[bold green]✅ Project '{app_name}' created successfully![/bold green]")
    console.print(f"[dim]→ Android project: [cyan]{android_dir.resolve()}[/cyan][/dim]")
    console.print(f"[dim]→ Python code:     [cyan]{main_dir.resolve()}[/cyan][/dim]")
    console.print(f"\n[dim]Run [cyan]cd {app_name}[/cyan] then [cyan]andropy build[/cyan][/dim]\n")