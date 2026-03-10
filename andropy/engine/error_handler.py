from rich.console import Console
from rich.panel import Panel

console = Console()


def show_compile_error(filename: str, message: str, hint: str = None):
    """Show friendly compile error."""
    content = f"[red]{message}[/red]"
    if hint:
        content += f"\n\n[yellow]Hint:[/yellow] {hint}"

    console.print(Panel(
        content,
        title=f"[bold red]❌ Compile Error — {filename}[/bold red]",
        border_style="red"
    ))


def show_config_error(field: str, message: str, hint: str = None):
    """Show friendly config error."""
    content = f"[red]{message}[/red]"
    if hint:
        content += f"\n\n[yellow]Hint:[/yellow] {hint}"

    console.print(Panel(
        content,
        title=f"[bold red]❌ Config Error — {field}[/bold red]",
        border_style="red"
    ))


def show_project_error(message: str, hint: str = None):
    """Show friendly project error."""
    content = f"[red]{message}[/red]"
    if hint:
        content += f"\n\n[yellow]Hint:[/yellow] {hint}"

    console.print(Panel(
        content,
        title="[bold red]❌ Project Error[/bold red]",
        border_style="red"
    ))


def show_build_error(message: str, hint: str = None):
    """Show friendly build error."""
    content = f"[red]{message}[/red]"
    if hint:
        content += f"\n\n[yellow]Hint:[/yellow] {hint}"

    console.print(Panel(
        content,
        title="[bold red]❌ Build Error[/bold red]",
        border_style="red"
    ))