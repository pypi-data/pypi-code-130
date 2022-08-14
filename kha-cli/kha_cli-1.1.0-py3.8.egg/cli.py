import json

import click

from kha import __version__
from kha.scripts.ssh import ssh
from kha.scripts.translate import t
from kha.scripts.ts import ts
from kha.utils.file_utils import exists, mkdirs
from kha.const import BASE_CONFIG_PATH, T_CONFIG_FILENAME


CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    default_map={
        't': {'key': 0, 'keyfrom': ''},
    }
)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', default=False)
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

    if not exists(BASE_CONFIG_PATH):
        mkdirs(BASE_CONFIG_PATH, all_dir=True)

    # read t config
    if exists(T_CONFIG_FILENAME):
        with open(T_CONFIG_FILENAME) as t_config:
            ctx.obj['t'] = json.load(t_config)

    @ctx.call_on_close
    def close():
        pass


@cli.command('greet', short_help='欢迎')
@click.option('--string', default='world')
@click.pass_context
def greet(ctx, string):
    click.echo()
    click.echo(f'🦄 hello, {string}.')
    click.echo()
    click.echo(json.dumps(ctx.obj, indent=2))
    click.echo()


cli.add_command(t)
cli.add_command(ts)
cli.add_command(ssh)


if __name__ == '__main__':
    cli()
