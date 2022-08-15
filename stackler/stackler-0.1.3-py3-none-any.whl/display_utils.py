"""
Display utils for better UX for Stackler
"""

from datetime import datetime
import sys
import os

from humanize import naturaltime
from git import Commit
from termcolor import colored

from stackler.git_utils import get_short_hash
from stackler.phab_utils import has_diff_attached, get_diff_id

DIFF_ID_LENGTH = 7  # Dxxxxxx


def _darken(in_s: str) -> str:
    """returns a darkened string"""
    return colored(in_s, attrs=['dark'])


def _underline(in_s: str) -> str:
    """returns an underlined string"""
    return colored(in_s, attrs=['underline'])


def _green(in_s: str) -> str:
    """returns a green string"""
    return colored(in_s, 'green')


def _red(in_s: str) -> str:
    """returns a red string"""
    return colored(in_s, 'red')


def _cyan(in_s: str) -> str:
    """returns a cyan string"""
    return colored(in_s, 'cyan')


def _yellow(in_s: str) -> str:
    """returns a yellow string"""
    return colored(in_s, 'yellow')


def _green(in_s: str) -> str:
    """returns a green string"""
    return colored(in_s, 'green')


def _blue(in_s: str) -> str:
    """returns a blue string"""
    return colored(in_s, 'blue')


def _truncate_string(str_input: str, max_length: str) -> str:
    str_end = '...'
    length = len(str_input)
    if length > max_length:
        return str_input[:max_length - len(str_end)] + str_end
    return str_input


def commit_summary(cmt: Commit, short=True) -> str:
    """Returns an inline summary of a given commit"""
    hsh = get_short_hash(cmt)
    author = cmt.author.name
    time = naturaltime(datetime.now() - cmt.committed_datetime.replace(tzinfo=None))
    status = get_diff_id(cmt) if has_diff_attached(cmt) else "N/A".center(DIFF_ID_LENGTH)

    term_width = os.get_terminal_size().columns
    msg = _truncate_string(cmt.message, term_width - DIFF_ID_LENGTH - len(hsh + author + time) - 10)
    msg = ' '.join(msg.split())

    hsh = _red(hsh)
    author = _cyan(author)
    time = _green(time)
    status = _yellow(status)

    if short:
        return f"<{hsh} {_truncate_string(msg, 20)}>"
    else:
        return f"{status} - {hsh} - {msg} ({time}) <{author}>"


def print_update_msg(current_commit: Commit, current_diff_id: str, update_message: str):
    """print msg for updating an diff"""
    print(
        f"{_blue('Update')} {_yellow(current_diff_id)} with"
        + f" {commit_summary(current_commit)}"
        + (f", message: {_truncate_string(update_message, 30) }." if update_message else "."))


def print_submit_msg(current_commit: Commit, prev_commit: Commit):
    """print msg for submitting an diff"""
    print(
        f"{_green('Submit')} {commit_summary(current_commit)}"
        + f" based on {commit_summary(prev_commit)}.")


def print_error(err_msg):
    """print msg to stderr"""
    print(_red(err_msg), file=sys.stderr)


def print_warning(err_msg):
    """print msg to stderr"""
    print(_yellow(err_msg), file=sys.stdout)
