import click

from .config import dump_json, make_client, write_table
from .entrypoint import cli


@cli.group()
def host():
    pass


@host.command(name="ls")
@click.option("--json", "-J", "print_json", default=False, type=bool, is_flag=True)
def list_hosts(print_json):
    hosts = make_client().list_hosts()
    if print_json:
        dump_json(hosts)

    table = [(hst.name, hst.slug, hst.id) for hst in hosts]
    write_table(table, ("Name", "Slug", "Id"))


@host.command(name="get")
@click.argument("host")
@click.option("--json", "-J", "print_json", default=False, type=bool, is_flag=True)
def get_host(host, print_json):
    client = make_client()
    host = client.get_host(host)

    if print_json:
        dump_json(host)

    click.echo(host.id, host.name)
