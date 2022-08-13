import logging
import os

import click

from composition.applications import Application
from composition.install import install_application
from composition.list import list_applications, setup_default_logging_format
from composition.uninstall import uninstall_application


@click.command("install")
@click.option("--template", "-t", default="template.yaml", help="The name of the template file to install")
@click.option("--value", "-v", default=["values.yaml"], help="A list of values files to generate templates from",
              multiple=True)
def install(template="template.yaml", value=None):
    """
    Install a docker-compose application using a given template.
    """
    logging.debug(f"Installing template {template}")
    logging.info(f"Hello, {os.getcwd()}, template {template}")
    install_application(template, value)


@click.command("uninstall")
@click.argument("application_name")
def uninstall(application_name):
    """
    Uninstalls a given application, removing it completely.
    """
    uninstall_application(application_name)


@click.command("list")
def list_all():
    """
    list installed applications
    """
    logging.debug("Listing...")
    list_applications()


@click.group()
@click.option("--verbose", default=False)
@click.option("--level", default="INFO", type=click.Choice(['DEBUG', 'INFO', 'ERROR']))
def cli(verbose, level):
    if verbose:
        level = logging.DEBUG

    # Set the default logging
    logging.basicConfig(level=level)
    logging.root.setLevel(level)
    # Remove the default formatting with log level
    setup_default_logging_format()
    # TODO remove
    Application("Prometheus")
    Application("Grafana")


def entrypoint():
    cli.add_command(install)
    cli.add_command(uninstall)
    cli.add_command(list_all)
    cli()


if __name__ == "__main__":
    entrypoint()
