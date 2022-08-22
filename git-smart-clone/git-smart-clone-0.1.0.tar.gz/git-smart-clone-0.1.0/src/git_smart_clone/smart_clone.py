import sys

import click
import os
import pathlib
import subprocess

import giturlparse

@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument("repo",type=str)
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def git_smart_clone(repo:str,args):
    print(args)
    home_folder = pathlib.Path.home()
    base_path = os.environ.get("GIT_SMART_CLONE_BASE_PATH",
                               home_folder / 'src')

    url = giturlparse.parse(repo)
    destination_path = base_path / url.resource / url.owner / url.name

    # make the path
    destination_path.mkdir(parents=True,exist_ok=True)
    git_args = ['git','clone',repo,destination_path.absolute()]
    git_args.extend(args)
    subprocess.run(git_args)





if __name__ == '__main__':
    git_smart_clone()
