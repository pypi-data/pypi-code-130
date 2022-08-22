import typer
import base64


app = typer.Typer()


@app.callback()
def callback():
    """
    Base64 Converter
    """


@app.command("e")
def encode(data_string: str):
    """
    Base64 encode
    """
    data_string_bytes = data_string.encode("ascii")

    base64_bytes = base64.b64encode(data_string_bytes)
    base64_string = base64_bytes.decode("ascii")

    typer.echo(f"{base64_string}")


@app.command("d")
def decode(base64_string: str):
    """
    Base64 decode
    """
    base64_bytes = base64_string.encode("ascii")

    data_string_bytes = base64.b64decode(base64_bytes)
    data_string = data_string_bytes.decode("ascii")

    typer.echo(f"{data_string}")
