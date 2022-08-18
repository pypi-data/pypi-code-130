"""Console script for zeroml."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("zeroml")
    click.echo("=" * len("zeroml"))
    click.echo("zeroml")


if __name__ == "__main__":
    main()  # pragma: no cover
