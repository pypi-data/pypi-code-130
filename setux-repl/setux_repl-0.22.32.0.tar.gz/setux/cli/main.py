from importlib.resources import read_text

from pybrary.command import Command

from ..cmd.cmd import CommandCmd
from ..cmd.deploy import  DeployCmd
from ..cmd.manage import  ManageCmd
from ..cmd.method import  MethodCmd
from ..cmd.target import  TargetParam
from ..cmd.config import get_config, ConfigCmd
from setux.repl.repl import repl


class UsageCmd(Command):
    '''Usage
    show usage
    '''
    vargs = True

    def run(self):
        from setux.main import banner
        tpl = read_text('setux.cli', 'usage.tpl')
        usage = tpl.strip().format(**locals())
        print(usage)


class MainCmd(Command):
    '''setux
    Setux commands
    '''
    shortcut = True
    subs = dict(
        command = CommandCmd(),
        deploy = DeployCmd(),
        manage = ManageCmd(),
        method = MethodCmd(),
    )


class ReplCmd(Command):
    '''REPL
    Setux REPL
    '''
    shortcut = True
    def run(self):
        target = self.get('target')
        cmd = MainCmd()
        cmd.parent = self.parent
        repl(target, cmd)


class CliCmd(Command):
    '''cli
    Setux cli
    '''
    Params = [
        TargetParam,
    ]
    config = get_config()
    subs = dict(
        repl = ReplCmd(),
        **MainCmd.subs,
    )
    shortcut = True


class TopCmd(Command):
    '''Setux Cli Top Command
    '''
    subs = dict(
        config = ConfigCmd(),
        cli = CliCmd(),
        usage = UsageCmd(),
    )
    shortcut = True


def top():
    cmd = TopCmd()
    cmd()



