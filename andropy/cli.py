import typer
from andropy.commands.create import create
from andropy.commands.compile import compile
from andropy.commands.build import build
from andropy.commands.clean import clean
from andropy.commands.run import run
from andropy.commands.sync import sync
from andropy.commands.setup import setup

app = typer.Typer(help="Andropy - Build native Android apps with Python")

app.command()(create)
app.command()(compile)
app.command()(build)
app.command()(clean)
app.command()(run)
app.command()(sync)
app.command()(setup)

if __name__ == "__main__":
    app()
