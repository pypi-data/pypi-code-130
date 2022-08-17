import click

import os.path
import json
import errno

from ._version import version as __version__  # noqa

API_ENDPOINT = "https://cchdo.ucsd.edu/api/v1"


def check_apikey():
    from cchdo.auth import get_apikey

    if get_apikey() == "":
        click.echo("Could not find an API key, have you run `uow bootstrap`?")
        exit(1)


def get_uow_info():
    """Walks up the directory tree until it either hits the root level or finds
    a ".uow_info" json file of the correct format

    Will exit if the cwd does not appear to be a uow or a subdir of one.

    :returns: a uow_info json and the path to the root of the uow
    """
    last_dir = os.getcwd()
    info_file = None
    if os.path.exists(os.path.join(last_dir, ".uow_info")):
        info_file = os.path.join(last_dir, ".uow_info")
    else:
        while last_dir != os.path.dirname(last_dir):
            last_dir = os.path.dirname(last_dir)
            if os.path.exists(os.path.join(last_dir, ".uow_info")):
                info_file = os.path.join(last_dir, ".uow_info")
                break
    if not info_file:
        print(f"{os.getcwd()} does not seem to be in a uow")
        raise click.Abort()

    try:
        with open(info_file, "r") as f:
            uow_info = json.load(f)
    except ValueError:
        print(f"Invalid uow_info file: {info_file}")
        raise click.Abort()

    if "cruise_id" not in uow_info:
        print(f"Invalid uow_info file: {info_file}")
        raise click.Abort()
    return uow_info, os.path.dirname(info_file)


def get_fetch_events():
    _, basedir = get_uow_info()

    # The fetch log will not exist if no fetches have been done so check for
    # the specific error no and then return an empty list
    # TODO Clean up this method when we move to python3
    fetch_log_path = os.path.join(basedir, ".fetch_log")
    try:
        with open(fetch_log_path, "r") as f:
            fetch_log = f.readlines()
    except IOError as e:
        if e.errno == errno.ENOENT:
            return []
        else:
            print(
                (
                    "Error while reading fetch log, please include the following "
                    "traceback with any bug reports:"
                )
            )
            raise
    # The fetch log is written with one json "object" per line, we also have
    # newlines on either side of the objects, it is also possible for a fetch
    # to have been abborted in the middle of a log write, so we only care about
    # the json objects we can actually read and can safly ignore everything
    # else
    fetch_events = []
    for log in fetch_log:
        try:
            fetch_events.append(json.loads(log))
        except ValueError:
            pass

    # Here we are taking advantage of the both the order of the fetch events
    # (later events come later) and dicts keeping the latest assignment for any
    # given key. This will will have both the latest unique fetches in it.
    unique_events = {}
    for event in fetch_events:
        unique_events[event["id"]] = event

    return unique_events.values()
