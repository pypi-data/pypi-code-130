import os

from subprocess import Popen, PIPE
from typing import Tuple


def delta_dict(first: dict, second: dict, verbose=False) -> Tuple[list, list, list]:
    """Returns difference between two dicts as "added", "removed" or "modified" items.

    Parameters
    ----------
    first : dict
        Base dictionary
    second : dict
        Dictionary to compare
    verbose : bool, optional
        Print information, by default False

    Returns
    -------
    Tuple[list, list, list]
        Tuple containing added, removed and modified keys respectively as individual lists
    """

    # Added keys
    added = []
    for key in second:
        if key not in first:
            added.append(key)
            if verbose:
                print("added", key)

    # Removed keys
    removed = []
    for key in first:
        if key not in second:
            removed.append(key)
            if verbose:
                print("removed", key)

    # Modified keys
    modified = []
    for key in first:
        if key in second:
            if first[key] != second[key]:
                modified.append(key)
                if verbose:
                    print("modified", key)

    return added, removed, modified


def delta_list(first: list, second: list, verbose=False) -> Tuple[list, list]:
    """Return difference between to lists as "added" and "removed" items.

    Parameters
    ----------
    first : list
        Base list
    second : list
        List to compare
    verbose : bool, optional
        Print information, by default False

    Returns
    -------
    Tuple[list, list]
        Tuple containing added and removed items respectively, as individual lists
    """

    # Added items
    added = []
    for item in second:
        if item not in first:
            added.append(item)
            if verbose:
                print("added", item)

    # Removed items
    removed = []
    for item in first:
        if item not in second:
            removed.append(item)
            if verbose:
                print("removed", item)

    return added, removed


def get_post_env(payload: str, shell: str, encoding="utf-8", char_equals="=", login_shell=True) -> dict:
    """Returns the environment variables after sourcing a given shell script as a dictionary.

    Parameters
    ----------
    payload : str
        Shell script to source, can be supplied with arguments
    shell : str
        Shell executable
    encoding : str, optional
        Encoding to be passed to subprocess library, by default "utf-8"
    char_equals : str, optional
        Character that specifies equality (used while parsing stdout), by default "="
    login_shell : bool, optional
        Use a login shell with a fresh environment, by default True. If False, inherited environment will be used before
        sourcing the payload.

    Returns
    -------
    dict
        Environment variables and their values after sourcing the payload
    """

    # Check if given shell exists
    if not os.path.isfile(shell):
        raise ValueError("Given shell executable {:s} not found!".format(shell))

    # Run the command in a new shell and collect the stdout
    if login_shell:
        command = "env -i HOME=\"$HOME\" {:s} -l -c 'source {:s} > /dev/null && env'".format(shell, payload)
    else:
        command = "{:s} -c 'source {:s} > /dev/null && env'".format(shell, payload)
    process = Popen(command, stdout=PIPE, shell=True, executable=shell)
    data = process.communicate()[0].decode(encoding)

    environment = {}
    for line in data.split(os.linesep):
        line_split = line.split(char_equals)
        try:
            k, v = line_split[0], line_split[1]
            if k and v:
                environment[k] = v
        except IndexError:
            continue

    return environment


def get_base_env(shell: str, encoding="utf-8", char_equals="=") -> dict:
    """Returns the default environment variables after creation of a login shell.

    Parameters
    ----------
    shell : str
        Shell executable
    encoding : str, optional
        Encoding to be passed to subprocess library, by default "utf-8"
    char_equals : str, optional
        Character that specifies equality (used while parsing stdout), by default "="

    Returns
    -------
    dict
        Environment variables and their values
    """

    # Check if given shell exists
    if not os.path.isfile(shell):
        raise ValueError("Given shell executable {:s} not found!".format(shell))

    command = "env -i HOME=\"$HOME\" {:s} -l -c 'env'".format(shell)
    process = Popen(command, stdout=PIPE, shell=True, executable=shell)
    data = process.communicate()[0].decode(encoding)

    environment = {}
    for line in data.split(os.linesep):
        line_split = line.split(char_equals)
        try:
            k, v = line_split[0], line_split[1]
            if k and v:
                environment[k] = v
        except IndexError:
            continue

    return environment


def delta_env_str(first: dict, second: dict, show_added_paths_seperately=True) -> str:
    """Returns (as a string) differences between two states of environment variables supplied as dictionaries.

    Parameters
    ----------
    first : dict
        Base state of user environment
    second : dict
        Post state of user environment
    show_added_paths_seperately : bool, optional
        If multiple paths are present in a variable places them in a new line, by default True

    Returns
    -------
    str
        Formatted string containing information about added, removed and modified environment variables
    """

    added, removed, modified = delta_dict(first, second)

    result = ""

    # Modified environment variables
    if (len(modified)) == 0:
        result += "There are no modified environment variables." + os.linesep
    else:
        result += "Modified environment variables" + os.linesep + 30 * "-" + os.linesep
    for key in modified:
        # Check if this environments variable refers to path(s) by counting dir seperators
        if second[key].count(os.sep) > 0:
            result += "  {:s}".format(key) + os.linesep
            # Get added and removed paths
            added_paths, removed_paths = delta_list(first[key].split(os.pathsep), second[key].split(os.pathsep))
            if show_added_paths_seperately:
                for path in added_paths:
                    result += "+ {:s}".format(path) + os.linesep
                for path in removed_paths:
                    result += "- {:s}".format(path) + os.linesep
            else:
                if added_paths:
                    result += "+ " + os.pathsep.join(added_paths) + os.linesep
                if removed_paths:
                    result += "- " + os.pathsep.join(removed_paths) + os.linesep
        # Non-path variables
        else:
            result += "  {:s}".format(key) + os.linesep
            result += "O {:s}".format(first[key]) + os.linesep
            result += "N {:s}".format(second[key]) + os.linesep

    # Added environment variables
    if len(added) == 0:
        result += os.linesep + "There are no added environment variables" + os.linesep
    else:
        result += os.linesep + "Added environment variables" + os.linesep + 27 * "-" + os.linesep
    for key in added:
        # Check if new environment variable contains multiple paths and we should print accordingly
        if second[key].count(os.pathsep) > 0 and show_added_paths_seperately:
            result += "+ {:s}".format(key) + os.linesep
            for path in second[key].split(os.pathsep):
                result += "  {:s}".format(path) + os.linesep
        else:
            result += "+ {:s}".format(key) + os.linesep
            result += "  {:s}".format(second[key]) + os.linesep

    # Removed environment variables
    if len(removed) == 0:
        result += os.linesep + "There are no removed environment variables." + os.linesep
    else:
        result += os.linesep + "Removed environment variables" + os.linesep + 29 * "-" + os.linesep
        for key in removed:
            result += "  {:s}".format(key) + os.linesep

    return result
