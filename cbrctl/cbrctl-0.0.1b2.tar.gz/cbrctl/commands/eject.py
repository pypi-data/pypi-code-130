import click
from cbrctl.platforms.eks import EKS_DECONFIG_ACTIONS
from cbrctl.utilities import run_shell_command

from logging import basicConfig, getLogger, INFO

formatter = " %(asctime)s | %(levelname)-6s | %(process)d | %(threadName)-12s |" \
            " %(thread)-15d | %(name)-30s | %(filename)s:%(lineno)d | %(message)s |"
basicConfig(level=INFO, format=formatter)
logger = getLogger(__name__)


@click.command(help="Uninstalls resources configured by Carbonara")
@click.option('-y', default=True, is_flag=True, prompt='Are you sure?', help='Confirmation')
def eject(y):
    if y == True:
        click.secho("Removing Carbonara resources...", fg='blue', bold=True)
        with click.progressbar(EKS_DECONFIG_ACTIONS) as bar:
            for action in bar:
                if (run_shell_command(action) != 0):
                    raise click.Abort
        click.secho("Cluster Cleaned Successfully. Happy Carbonara \m/", fg='blue')
    else:
        click.echo('Aborted!')