import typer

from . import main


app = typer.Typer(pretty_exceptions_enable=False)
app.command()(main)
app()
