import os

import click


@click.group
@click.option("--file", "-f", "config_file", type=click.Path(), required=False)
@click.pass_context
def cli(ctx, config_file):
    ctx.ensure_object(dict)

    ctx.obj["config_file"] = config_file
    ctx.obj["config_file_set"] = config_file is not None

    config_file = config_file or os.path.join(os.path.expanduser("~"), ".weevils.conf")
    ctx.obj["config_file"] = config_file

    if os.path.exists(config_file):
        ctx.obj["config"] = None  # Configuration(config_file)
    else:
        ctx.obj["config"] = None


if __name__ == "__main__":
    cli()
