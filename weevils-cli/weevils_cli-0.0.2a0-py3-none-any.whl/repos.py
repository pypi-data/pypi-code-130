import sys

import click

from .config import dump_json, make_client
from .entrypoint import cli
from .utils import is_uuid


@cli.group()
def repo():
    pass


@repo.command
@click.option("--host", "-h", type=str, default=None)
@click.option("--owner", "-o", type=str, default=None)
@click.option("--repo", "-r", type=str, default=None)
@click.option("--show-json", "-J", type=bool, is_flag=True, default=False)
@click.option("--only-id", "-I", type=bool, is_flag=True, default=False)
def get(host: str, owner: str, repo: str, show_json: bool, only_id: bool):
    client = make_client()

    if host is None:
        click.echo("Host not specified; defaulting to GitHub")
        host = "github"

    host = client.get_host(host)

    if owner is None and not is_uuid(repo):
        click.echo("Must specify either an owner name and repository name as strings, or a repository ID")

    if owner and repo:
        repo = host.repository(owner, repo)
    else:
        repo = host.repository_by_id(repo)

    if only_id:
        click.echo(repo.id)
        sys.exit(0)

    if show_json:
        dump_json(repo)
        sys.exit(0)

    click.echo("hello")
