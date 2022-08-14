from pybrary.command import Command, Param, ValidationError

from setux.core.manage import Manager
from setux.core.module import Module
from ..cmd.cmd import get_commands


usage = '''
commands
    list available commands

managers
    list available managers

modules
    list available modules

mappings
    list available mappings

help "commad"
    show "command" help

help "manager"
    show "manager" help

help "module"
    show "module" help
'''


class Obj(Param):
    '''name
    '''
    name = 'help_obj'
    positional = True

    def verify(self, name):
        target = self.get('target')
        commands = get_commands()
        if name in commands:
            return commands[name]()
        obj = target.managers.get(name)
        if obj:
            return obj
        obj = target.modules.items.get(name)
        if obj:
            return obj(target.distro)
        raise ValidationError(f"{name} not found")


def header(txt):
    print(txt)
    print('-'*len(txt))


class Help(Command):
    '''Show Help
    '''
    Params = [
        Obj,
    ]

    def run(self):
        target = self.get('target')
        obj = self.get('help_obj')
        '''
        if version_info >= (3, 10):
            match obj:
                case Command() as command:
                    header(f'Command {command.__class__.__name__}')
                    command.help(fetch=False)
                case Manager() as manager:
                    header(f'{manager}'.replace('.', ' '))
                    manager.help()
                case Module() as module:
                    header(f'Module {module.__module__.split(".")[-1]}')
                    module.help()
                case _:
                    print(usage)
        else:
        '''
        if isinstance(obj, Command):
            command = obj
            header(f'Command {command.__class__.__name__}')
            command.help(fetch=False)
        elif isinstance(obj, Manager):
            manager = obj
            header(f'{manager}'.replace('.', ' '))
            manager.help()
        elif isinstance(obj, Module):
            module = obj
            header(f'Module {module.__module__.split(".")[-1]}')
            module.help()
        else:
            print(usage)

