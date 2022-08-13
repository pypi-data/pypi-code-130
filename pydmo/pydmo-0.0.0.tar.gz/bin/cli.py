#! /usr/bin/env python
import click
from dotenv import load_dotenv

from pydmo.utils import hello

# see `.env` for requisite environment variables
load_dotenv()


@click.group()
@click.version_option(package_name="pydmo")
def cli():
    pass


@cli.command()
def main() -> None:
    """pydmo Main entrypoint"""
    click.secho(hello(), fg="green")


if __name__ == "__main__":
    cli()
