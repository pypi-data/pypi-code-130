import json

import click

from .config import make_client
from .entrypoint import cli
from .utils import is_uuid


@cli.group()
def job():
    pass


@job.command
@click.argument("job", type=str, default=None)
@click.option("--show-json", "-J", type=bool, is_flag=True, default=False)
@click.option("--output", "-o", type=bool, is_flag=True, default=False)
def get(job: str, show_json: bool, output: bool):
    client = make_client()

    if not is_uuid(job):
        raise ValueError

    job = client.get_job(job)

    if output:
        click.echo(job.output)
    elif show_json:
        click.echo(json.dumps(job.raw, indent=2))
    else:
        click.echo(job)
