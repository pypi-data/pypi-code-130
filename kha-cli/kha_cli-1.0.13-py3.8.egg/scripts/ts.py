import time
from datetime import datetime

import click

from kha.const import FORMAT_DATETIME


@click.command('ts', short_help='时间戳')
@click.argument('text', nargs=-1, type=str)
@click.pass_context
def ts(ctx, text):
    click.echo()
    if len(text) == 2:
        dt_str = ' '.join(text)
        if len(dt_str) == 19:
            try:
                click.echo(int(datetime.strptime(dt_str, FORMAT_DATETIME).timestamp() * 1000))
                click.echo()
                return
            except Exception as e:
                pass

    if len(text) == 1:
        text = text[0]
        if text.isdigit() and len(text) == 10:
            try:
                click.echo(time.strftime(FORMAT_DATETIME, time.localtime(int(text))))
                click.echo()
                return
            except Exception as e:
                pass

        if text.isdigit() and len(text) == 13:
            try:
                click.echo(time.strftime(FORMAT_DATETIME, time.localtime(int(text) / 1000)))
                click.echo()
                return
            except Exception as e:
                pass

    click.echo('🦄 没预设的参数')
    click.echo()
