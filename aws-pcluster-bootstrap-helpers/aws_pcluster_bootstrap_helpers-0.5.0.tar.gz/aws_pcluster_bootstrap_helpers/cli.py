"""Console script for aws_pcluster_bootstrap_helpers."""
import os

import rich_click as click
from rich_click import RichCommand, RichGroup

from aws_pcluster_bootstrap_helpers.commands import cli_build_ami


@click.group()
def cli():
    """
    Helper functions for aws parallelcluster.
    """
    return


@cli.command()
@click.option('--output', help="Path to output pcluster describe-image", required=True,
              default=os.environ.get('PCLUSTER_BUILD_AMI_FILE'))
@click.option('--region', help="Aws region to query", required=False, default=os.environ.get('AWS_DEFAULT_REGION'))
@click.option("--image-id", help="Ami build ID", required=True, default=os.environ.get('PCLUSTER_BUILD_AMI_ID'))
def build_ami_watcher(output, region, image_id):
    """Watcher for PCluster image builder"""
    click.echo("PCluster image builder watcher")
    cli_build_ami.main(image_id=image_id, output_file=output, region=region)


if __name__ == "__main__":
    cli()
