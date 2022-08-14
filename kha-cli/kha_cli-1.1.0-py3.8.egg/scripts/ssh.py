import click


@click.command()
@click.pass_context
def ssh(ctx):
    click.echo('ssh')
