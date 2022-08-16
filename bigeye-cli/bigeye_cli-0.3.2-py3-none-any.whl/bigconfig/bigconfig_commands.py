import typer

from bigeye_cli.functions import cli_client_factory
from bigeye_sdk.controller.metric_suite_controller import execute_bigconfig
from bigeye_sdk.log import get_logger

log = get_logger(__file__)

app = typer.Typer(no_args_is_help=True, help='Bigconfig Commands for Bigeye CLI')

"""
File should contain commands relating to deploying Bigconfig files.
"""


@app.command()
def plan(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        input_path: str = typer.Option(
            None
            , "--input_path"
            , "-ip"
            , help="(Optional) Input path containing Bigconfig files.  If no input path is defined then current"
                   "working directory will be used."),
        output_path: str = typer.Option(
            None
            , "--output_path"
            , "-op"
            , help="(Optional) Output path where reports and fixme files will be saved.  If no output path is defined "
                   "then current working directory will be used."),

):
    """Executes a plan for bigconfig files in the input path/current working directory."""
    client = cli_client_factory(bigeye_conf)
    execute_bigconfig(client=client, input_path=input_path, output_path=output_path)


@app.command()
def apply(
        bigeye_conf: str = typer.Option(
            None
            , "--bigeye_conf"
            , "-b"
            , help="Bigeye Basic Auth Configuration File"),
        input_path: str = typer.Option(
            None
            , "--input_path"
            , "-ip"
            , help="(Optional) Input path containing Bigconfig files.  If no input path is defined then current"
                   "working directory will be used."),
        output_path: str = typer.Option(
            None
            , "--output_path"
            , "-op"
            ,
            help="(Optional) Output path where reports and fixme files will be saved.  If no output path is defined "
                 "then current working directory will be used."),

):
    """Applies Bigconfig files from the input path/current working directory to the Bigeye workspace."""
    client = cli_client_factory(bigeye_conf)
    execute_bigconfig(client=client, input_path=input_path, output_path=output_path, apply=True)
