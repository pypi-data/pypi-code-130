#!/usr/bin/env python3
import re
import os
import sys
import time
import arrow
import shutil
from pathlib import Path
import json
import inquirer
import click
import subprocess
from . import cli
from .config import pass_config
from .config import Config

def get_sources(ctx, args, incomplete):
    config = Config()
    keys = config.sources.keys()
    if incomplete:
        keys = list(filter(lambda x: x.startswith(incomplete), keys))
    return keys


@cli.command()
@pass_config
def fetch(config):
    pass

def _get_files(config, shell):
    files = list(filter(bool, shell(["ls", "-tr", config['path']])))
    for file in files:
        if re.findall(config.get('regex', '.*'), file):
            yield file

def transfer(config, filename):
    destination = os.path.expanduser(config['destination'])
    subprocess.run([
        "rsync",
        f"{config['host']}:{config['path']}/{filename}",
        destination,
        "-arP"
    ])

@cli.command(help="Choose specific file to download")
@click.argument('source', required=True, autocompletion=get_sources)
@pass_config
def choose(config, source):
    config.source = source
    with config.shell() as (config, shell):
        files = list(_get_files(config, shell))
        answer = inquirer.prompt([
            inquirer.List('file', "Please choose:", choices=list(reversed(files)))
        ])
        if not answer:
            sys.exit(0)
        file = answer['file']
        transfer(config, file)

@cli.command()
@click.option('-s', '--source', required=True)
@click.option('-f', '--filename', required=True)
@click.option('-H', '--host', required=True)
@click.option('-U', '--username', required=False)
@click.option('-r', '--regex', required=True, default=".*")
@click.option('-p', '--path', required=True)
@click.option('-d', '--destination', required=True)
@pass_config
def add(config, source, filename, host, username, regex, path, destination):
    config.source = source
    config.add(
        filename=filename,
        host=host,
        username=username,
        path=path,
        regex=regex,
        destination=destination,
        )
    click.secho("Added host.", fg='green')

@cli.command()

@pass_config
@click.argument('source', required=True, autocompletion=get_sources)
def fetch(config, source):
    config.source = source
    with config.shell() as (config, shell):
        files = list(_get_files(config, shell))
        if not files:
            click.secho("No files found.")
            sys.exit(1)
        file = files[-1]
        transfer(config, file)

@click.option(
    "-x",
    "--execute",
    is_flag=True,
    help=("Execute the script to insert completion into users rc-file."),
)
def completion(execute):
    shell = os.environ["SHELL"].split("/")[-1]
    rc_file = Path(os.path.expanduser(f"~/.{shell}rc"))
    line = f'eval "$(_/\w+/\u/g_COMPLETE={shell}_source /\w+/\u/g)"'
    if execute:
        content = rc_file.read_text().splitlines()
        if not list(
            filter(
                lambda x: line in x and not x.strip().startswith("#"),
                content,
            )
        ):
            content += [f"\n{line}"]
            click.secho(
                f"Inserted successfully\n{line}"
                "\n\nPlease restart you shell."
                )
            rc_file.write_text('\n'.join(content))
        else:
            click.secho("Nothing done - already existed.")
    else:
        click.secho("\n\n" f"Insert into {rc_file}\n\n" f"echo '{line}' >> {rc_file}" "\n\n")
