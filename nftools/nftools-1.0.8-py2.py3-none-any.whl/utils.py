import logging
import re
import sys
from subprocess import run
from typing import List

from nftools.objects import ExtendedCompletedProcess

logger = logging.getLogger(__name__)


def query_yes_no(question, default=None, break_message=None):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            is_valid = valid[choice]
            if break_message and not is_valid:
                logger.warning(f'Exiting Peacefully: {break_message}')
                sys.exit(0)
            return is_valid
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def shorten_rpc(v):
    return f'{v[0:15]}...{v[len(v) - 10:]}'


def string_between(search, start: str, end: str):
    """Given a string and two sub strings, return the string between the two substings.

        :param search: str
        :param start: str
        :param end: str

        :return: str

        >>> string_between('ioo2i3jFIRSTbetweenSECOND', 'FIRST', 'SECOND')
        'between'
    """
    try:
        return re.search(f'{start}(.*){end}', search).group(1)
    except AttributeError:
        logger.warning(
            f'String [{search.encode("utf-8")}] does not contain a string seperated by ({start.encode("utf-8")}, {end.encode("utf-8")})')
        return None


def extract_signature(msg):
    return msg.split('Signature: ')[1]


def run_command(command) -> ExtendedCompletedProcess:
    result = ExtendedCompletedProcess(run(command, capture_output=True))
    return result


def format_command_str(commands: List):
    return f'[$ {" ".join(commands)}]'
