# these commands "inherit" from the base directly so that there is no 'weevils weevils ls' type commands
import sys
import time

import click
from weevils import WeevilsClient
from weevils.models import Weevil

from .config import dump_json, make_client, write_table
from .entrypoint import cli
from .utils import Spinner, is_uuid


def _find_weevil(client: WeevilsClient, id_or_slug: str) -> Weevil:
    if is_uuid(id_or_slug):
        return client.get_weevil(id_or_slug)

    for weev_obj in client.list_weevils():
        if id_or_slug in (weev_obj.id, weev_obj.slug, weev_obj.name):
            return weev_obj

    raise ValueError(f"Could not find weevil {id_or_slug}")


@cli.command(name="ls")
@click.option("--json", "-J", "print_json", default=False, type=bool, is_flag=True)
def list_weevils(print_json):
    weevils = make_client().list_weevils()

    if print_json:
        dump_json(weevils)

    table = [(weevil.name, weevil.slug, weevil.id) for weevil in weevils]
    table.sort(key=lambda x: x[1])
    write_table(table, ("Name", "Slug", "Id"))


@cli.command
@click.argument("name_or_id", type=str)
def get(name_or_id: str):
    client = make_client()
    weevil = _find_weevil(client, name_or_id)

    dump_json(weevil)


@cli.command
@click.argument("weevil", type=str)
@click.option("--host", "-h", type=str, default=None)
@click.option("--owner", "-o", type=str, default=None)
@click.option("--repo", "-r", type=str, default=None)
@click.option("--url", "-u", type=str, default=None)
@click.option("--detach", "-d", type=bool, is_flag=True, default=False)
# @click.argument("posargs", type=click.Tuple([str]), default=None, required=False)
def run(weevil: str, host: str, owner: str, repo: str, url: str, detach: bool):

    client = make_client()

    if host is None:
        click.echo("Host not specified; defaulting to GitHub")
        host = "github"

    host = client.get_host(host)

    # validate the arguments given
    if url is None:
        if owner is None and not is_uuid(repo):
            click.echo(owner, repo, is_uuid(repo))
            click.echo("Must specify a repo either by owner name and repository name, or with the repository ID")
            raise ValueError

        if is_uuid(repo):
            repo_id = repo
        else:
            repo_id = host.repository(owner, repo).id

    else:
        click.echo("Todo: URLs")
        raise ValueError

    weevil = _find_weevil(client, weevil)
    job_id = weevil.run(repo_id).id

    if detach:
        click.echo(f"Created job with ID {job_id}")
        sys.exit(0)

    click.echo(f"Running job {job_id}")
    with Spinner() as spinner:
        while True:
            job = client.get_job(job_id)
            spinner.update()

            if job.status in ("Success", "Failed"):
                break
            # TODO : some absolute timeout for client side too
            time.sleep(1)

    click.echo(job.output)


@cli.command
@click.argument("name", type=str)
@click.option("--base", "-b", type=str)
@click.option("--slug", "-s", type=str, required=False)
def create(name, base, slug):

    if base is None:
        raise ValueError("Must specifiy a base ID or slug")
    client = make_client()
    for base_obj in client.list_bases():
        if base in (base_obj.id, base_obj.slug):
            break
    else:
        raise ValueError(f"Could not find base {base}")

    if sys.stdin.isatty():
        script = click.edit()
    else:
        script = sys.stdin.read()

    if script is None:
        click.echo("No script was entered")
        sys.exit(1)

    weevil = client.create_weevil(name, base_obj, script, slug=slug)

    dump_json(weevil)


@cli.command
@click.argument("weevil", type=str)
def edit(weevil):
    client = make_client()
    weevil = _find_weevil(client, weevil)

    if sys.stdin.isatty():
        script = click.edit(text=weevil.script)
    else:
        script = sys.stdin.read()

    if script is None:
        click.echo("No changes made")
        sys.exit(0)

    weevil = client.update_weevil(weevil, script)
    dump_json(weevil)


# ---
# Base weevils
# ---
@cli.group()
def base():
    pass


@base.command(name="ls")
@click.option("--id-only", "-I", type=bool, default=False, is_flag=True)
def ls_bases(id_only):
    base_list = make_client().list_bases()

    if id_only:
        for base in base_list:
            click.echo(base.id)
        sys.exit(0)

    table = [(base.name, base.slug, base.id) for base in base_list]
    write_table(table, ("Name", "Slug", "Id"))
