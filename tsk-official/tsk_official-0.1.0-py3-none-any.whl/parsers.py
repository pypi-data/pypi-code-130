from argparse import ArgumentParser

from tsk.enums import Selector
from tsk import transforms
from tsk.settings import Settings
from tsk import commands


conf = Settings()

def construct(subparser, name: str, **kwargs):
    # create base parser with name and aliases
    base_parser = subparser.add_parser(name, **kwargs)

    # add arguments to the parser
    if name == 'add':
        _construct_add_parser(base_parser)
    elif name == 'complete':
        _construct_complete_parser(base_parser)
    elif name == 'remove':
        _construct_remove_parser(base_parser)
    elif name == 'update':
        _construct_update_parser(base_parser)
    elif name == 'list':
        _construct_list_parser(base_parser)
    elif name == 'wipe':
        _construct_wipe_parser(base_parser)
    elif name == 'config':
        _construct_config_parser(base_parser)

    # link the command name to a function to execute
    base_parser.set_defaults(func=commands.cmd_map[name])

def _construct_add_parser(p: ArgumentParser):
    p.add_argument('selector', type=Selector,
                   choices=[s for s in Selector])
    p.add_argument('title', type=str,
                   help='name of the task')
    p.add_argument('-l', type=str,
                   default=conf['TaskDefaults']['tasklist_id'],
                   dest='tasklist_id',
                   help='id of the tasklist to add the task to')
    p.add_argument('-p', '--priority', type=int,
                   default=conf['TaskDefaults']['priority'],
                   choices=range(0, 4),
                   dest='task_priority',
                   help='priority of the task')
    p.add_argument('-d', '--duedate', type=transforms.mkdate,
                   dest='task_date_due',
                   default=conf.get_default_val('date_due'),
                   help='date the task should be completed by')
    p.add_argument('-n', '--notes', type=str,
                   default='',
                   dest='task_notes',
                   help='additional task information')

def _construct_complete_parser(p: ArgumentParser):
    p.add_argument('ids', type=str,
                   nargs='+',
                   help='id(s) of the task(s) to complete')
    p.add_argument('-u', '--uncomplete', action='store_false',
                   dest='is_set_complete',
                   help='undo completion status')

def _construct_remove_parser(p: ArgumentParser):
    p.add_argument('selector', type=Selector,
                   choices=[s for s in Selector])
    p.add_argument('ids', type=str,
                   nargs='+',
                   help='id(s) of the task(s)/tasklist(s)')

def _construct_update_parser(p: ArgumentParser):
    p.add_argument('selector', type=Selector,
                   choices=[s for s in Selector])
    p.add_argument('id', type=str,
                   help='id of the task/tasklist to update')
    p.add_argument('-t', '--title', type=str,
                   help='name of the task/tasklist')
    p.add_argument('--make-default', action='store_true',
                   dest='tasklist_make_default',
                   help='make this tasklist the default tasklist')
    p.add_argument('-p', '--priority', type=int,
                   choices=range(1, 4),
                   dest='task_priority',
                   help='priority of the task')
    p.add_argument('-d', '--duedate', type=transforms.mkdate,
                   dest='task_date_due',
                   help='date the task should be completed by')
    p.add_argument('-n', '--notes', type=str,
                   dest='task_notes',
                   help='additional task information')

def _construct_list_parser(p: ArgumentParser):
    p.add_argument('tasklist_id', type=str,
                   nargs='?',
                   help='id of the tasklist')

def _construct_wipe_parser(p: ArgumentParser):
    pass

def _construct_config_parser(p: ArgumentParser):
    p.add_argument('section', type=str,
                   choices=['TaskDefaults', 'View'])
    p.add_argument('key', type=str)
    p.add_argument('value', type=str)
