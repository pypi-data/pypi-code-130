import sys

import click
import os
import pathlib
import subprocess

import giturlparse


def parse_git_url(url: str) -> giturlparse.parser.Parsed:
    parsed_url = giturlparse.parse(url)

    if 'sr.ht' in url:
        return giturlparse.parser.Parsed(
            parsed_url.pathname,
            parsed_url.protocols,
            parsed_url.protocol,
            parsed_url.href,
            'sr.ht',
            parsed_url.user,
            parsed_url.port,
            parsed_url.name,
            parsed_url.resource
        )

    return parsed_url

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument("repo",type=str)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def git_smart_clone(repo:str,args):
    home_folder = pathlib.Path.home()
    base_path = os.environ.get("GIT_SMART_CLONE_BASE_PATH",
                               home_folder / 'src')

    url = parse_git_url(repo)
    destination_path = base_path / url.resource / url.owner / url.name

    # make the path
    destination_path.mkdir(parents=True,exist_ok=True)
    git_args = ['git','clone',repo,destination_path.absolute()]
    git_args.extend(args)
    subprocess.run(git_args)





if __name__ == '__main__':
    git_smart_clone()
