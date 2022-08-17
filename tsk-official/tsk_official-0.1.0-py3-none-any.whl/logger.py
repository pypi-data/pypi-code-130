from typing import List, Union

from tsk.models.task import Task
from tsk.models.tasklist import Tasklist
from tsk.enums import Selector
from tsk.utils import tstamp_to_friendly_datestr
from tsk.settings import Settings


conf = Settings()

def print_tasklist(tasklist: Tasklist):
    """Outputs the tasklist in a pretty format."""

    oput_is_default = '(default)' \
        if tasklist.id == conf['TaskDefaults']['tasklist_id'] else ''
    print(f'{tasklist.title} ({tasklist.id}) {oput_is_default}')

def print_task(task: Task):
    """Outputs the task in a pretty format"""

    if not conf.getboolean('View', 'show_completed') and task.is_completed:
        return

    oput_is_completed = '*' if task.is_completed else ' '
    if task.priority == 3: oput_priority = '!'
    elif task.priority == 2: oput_priority = '^'
    elif task.priority == 1: oput_priority = '.'
    elif task.priority == 0: oput_priority = ' '
    oput_date_due = f'\n      {tstamp_to_friendly_datestr(task.date_due)}' \
        if task.date_due is not None else ''
    oput_notes = '{...}' if task.notes else ''
    
    task_oput = f'[{oput_is_completed}] ' \
                f'{task.title:-<35} ' \
                f'{oput_priority} ' \
                f'({task.id}) ' \
                f'{oput_notes}' \
                f'{oput_date_due}'
    print(task_oput)

def feedback_add(selector: Selector, item: Union[Tasklist, Task],
                 tasklist_title=None):
    """Provides feedback for the "add" command"""

    print(f'Added {selector.value} "{item.title}"', end='')
    if isinstance(item, Tasklist):
        print()
        print_tasklist(item)
    else:  # item is Task
        print(f' to tasklist "{tasklist_title}"')
        print_task(item)

def feedback_complete(tasks: List[Task], completed: bool):
    """Provides feedback for the "complete" command."""

    oput_complete_msg = 'Completed' if completed else 'Uncompleted'
    task_titles = [task.title for task in tasks]
    print(f'{oput_complete_msg} tasks ', end='')
    for count, title in enumerate(task_titles, 1):
        end_mark = ', ' if count != len(task_titles) else '\n'
        print(f'"{title}"{end_mark}', end='')
