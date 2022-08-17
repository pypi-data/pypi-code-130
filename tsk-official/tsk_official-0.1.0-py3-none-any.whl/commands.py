from argparse import Namespace, ArgumentError
from tsk.database.tsk_database import TskDatabase

from tsk.enums import Selector
from tsk.models.task import Task
from tsk.models.tasklist import Tasklist
from tsk import logger
from tsk.settings import Settings


conf = Settings()

def add(args: Namespace, db: TskDatabase):
    """Add task(s) or tasklist(s)."""

    if args.selector == Selector.Task:
        if not db.is_tasklist(args.tasklist_id):
            raise ArgumentError(None,
                                f'Tasklist id "{args.tasklist_id}" not found')
        
        task = Task(
            args.tasklist_id,
            args.title,
            priority=args.task_priority,
            date_due=args.task_date_due,
            notes=args.task_notes
        )
        db.add_task(task)
        logger.feedback_add(
            args.selector,
            task,
            tasklist_title=db.get_tasklists([task.tasklist_id])[0].title
        )
    
    elif args.selector == Selector.Tasklist:
        tasklist = Tasklist(args.title)
        db.add_tasklist(tasklist)
        logger.feedback_add(args.selector, tasklist)

def complete(args: Namespace, db: TskDatabase):
    """Complete task(s)."""

    db.set_tasks_completion(args.ids, args.is_set_complete)
    logger.feedback_complete(db.get_tasks_by_ids(args.ids), args.is_set_complete)

def remove(args: Namespace, db: TskDatabase):
    """Remove task(s) or tasklist(s)."""

    if args.selector == Selector.Task:
        db.remove_tasks(args.ids)
    elif args.selector == Selector.Tasklist:
        db.remove_tasklists(args.ids)

def update(args: Namespace, db: TskDatabase):
    """Update task(s) or tasklist(s)."""

    if args.selector == Selector.Task:
        db.update_task(
            args.id,
            title=args.title,
            priority=args.task_priority,
            date_due=args.task_date_due,
            notes=args.task_notes
        )
    elif args.selector == Selector.Tasklist:
        db.update_tasklist(
            args.id,
            title=args.title
        )
        if args.tasklist_make_default and db.is_tasklist(args.id):
            conf['TaskDefaults']['tasklist_id'] = args.id
            conf.commit()

def list(args: Namespace, db: TskDatabase):
    """List tasks(s) or tasklist(s)."""
    
    if args.tasklist_id:
        if not db.is_tasklist(args.tasklist_id):
            raise ArgumentError(None, f'Tasklist id "{args.tasklist_id}" not found')

        tasklist = db.get_tasklists([args.tasklist_id])
        if tasklist:
            tasklist = tasklist[0]
            logger.print_tasklist(tasklist)
            tasks = db.get_tasks(args.tasklist_id)
            for task in tasks:
                logger.print_task(task)
            
    else:  # print all the tasklists if no id was specified
        tasklists = db.get_tasklists()
        for tasklist in tasklists:
            logger.print_tasklist(tasklist)
            tasks = db.get_tasks(tasklist.id)
            for task in tasks:
                logger.print_task(task)

def wipe(args: Namespace, db: TskDatabase):
    """Remove all tasklists and tasks."""

    resp = input('Remove all tasklists and tasks? [Y/n] ')
    if not resp or resp.lower() == 'y':
        db.wipe()
        print('Removed all tasklists and tasks')

def config(args: Namespace, db: TskDatabase):
    """Configure task defaults and view options."""

    if args.section == 'TaskDefaults':
        if args.key == 'tasklist_id' and not db.is_tasklist(args.value):
            raise ArgumentError(None, 'tasklist_id must match a valid tasklist')
        elif args.key == 'priority' and (args.value < '0' or args.value > '3'):
            raise ArgumentError(None, 'priority must be between 1 and 3; use 0 if no default priority is desired')
        elif args.key == 'date_due' and int(args.value) < -1:
            raise ArgumentError(None, 'date_due must be greater than -1; use -1 if no default date_due is desired')
        elif args.key not in conf['TaskDefaults']:
            raise ArgumentError(None, f'{args.key} does not match a key in TaskDefaults')
    elif args.section == 'View':
        if args.key == 'show_completed' and (args.value != 'true' and args.value != 'false'):
            raise ArgumentError(None, 'show_completed must be set to either "true" or "false"')
        elif args.key not in conf['View']:
            raise ArgumentError(None, f'{args.key} does not match a key in View')
            
    conf[args.section][args.key] = args.value
    conf.commit()


cmd_map = {
    'add': add,
    'complete': complete,
    'remove': remove,
    'update': update,
    'list': list,
    'wipe': wipe,
    'config': config,
}
