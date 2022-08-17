import argparse

from tsk import parsers
from tsk.database.tsk_database import TskDatabase

def main():
    parser = argparse.ArgumentParser(
        prog='tsk',
        description='add, remove, and complete tasks seamlessly'
    )

    tsk_db = TskDatabase()
    subparser = parser.add_subparsers(dest='command')

    # add: adds a task
    parsers.construct(subparser, 'add', aliases=['a'])

    # complete: marks a task as completed
    parsers.construct(subparser, 'complete', aliases=['cm'])

    # remove: deletes task(s)/tasklist(s)
    parsers.construct(subparser, 'remove', aliases=['rm'])

    # update: update task/tasklist data
    parsers.construct(subparser, 'update', aliases=['up'])

    # list: list tasklist(s) data
    parsers.construct(subparser, 'list', aliases=['ls'])

    # wipe: remove all tasklists and tasks
    parsers.construct(subparser, 'wipe')

    # config: change task defaults and view options
    parsers.construct(subparser, 'config')


    # parse args
    args = parser.parse_args()

    args.func(args, tsk_db)
