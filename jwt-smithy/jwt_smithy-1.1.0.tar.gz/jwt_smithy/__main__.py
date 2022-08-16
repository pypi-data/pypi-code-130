import typer

from jwt_smithy.ecdsa import save_ecdsa_keys
from jwt_smithy.rsa import save_rsa_keys
from jwt_smithy.shmac import save_shmac_keys

app = typer.Typer()


@app.command(name="rsa")
def rsa_command(directory: str = "rsa"):
    """
    Generate rs256 key pair in the given directory.
    """
    save_rsa_keys(directory)


@app.command(name="ecdsa")
def ecdsa_command(directory: str = "ecdsa"):
    """
    Generate ec256 key pair in the given directory.
    """
    save_ecdsa_keys(directory)


@app.command(name="shmac")
def shmac_command(directory: str = "shmac"):
    """
    Generate sh256 key in the given directory.
    """
    save_shmac_keys(directory)


if __name__ == "__main__":
    app()
