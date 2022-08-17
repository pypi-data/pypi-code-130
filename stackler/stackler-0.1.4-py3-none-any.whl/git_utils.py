"""Git utils for Stackler"""

import os

from typing import Optional
from git import Commit, GitCommandError, Repo

REPO_PATH = os.getcwd()
BASE_TAG = "origin/develop"


def get_short_hash(cmt: Commit):
    """
    Returns the short unique hash
    """
    repo = Repo(REPO_PATH)
    return repo.git.rev_parse(cmt, short=True)


def is_unstaged():
    """
    Returns if there's unstaged files
    """
    repo = Repo(REPO_PATH)
    return len(repo.untracked_files) > 0


def is_detached():
    """
    Returns if the head is detached.
    """
    repo = Repo(REPO_PATH)
    return repo.head.is_detached


def is_dirty():
    """
    Returns if the changeset is not empty.
    """
    repo = Repo(REPO_PATH)
    return repo.is_dirty()


def get_commit_safe(sha: str) -> Optional[Commit]:
    """
    Gets the commit; exits gracefully if the commit is not found.
    """
    repo = Repo(REPO_PATH)
    try:
        return repo.commit(sha)
    except GitCommandError:
        return None


def is_commit_in_stack(sha: str, tip: str = None, base: str = BASE_TAG):
    """
    Returns if the commit is not in the range specified.
    """
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits(f"{base}..{tip}"))
    target_commit = get_commit_safe(sha)
    if not target_commit:
        return False
    return target_commit in commits
