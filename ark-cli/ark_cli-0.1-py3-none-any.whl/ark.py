# coding: utf-8

import click
from src.model.project import Project


@click.group()
@click.pass_context
def cli(ctx):
    """ark - Command line tool to manage ark app"""
    ctx.obj = Project()


@cli.command()
@click.pass_obj
def init(project: Project):
    print(project.dir())

