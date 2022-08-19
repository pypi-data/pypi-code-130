"""Console script for enterprise_search."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("enterprise_search")
    click.echo("=" * len("enterprise_search"))
    click.echo("Enterprise search CLI")


if __name__ == "__main__":
    main()  # pragma: no cover
