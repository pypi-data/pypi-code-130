#!/usr/bin/env python3
"""
Git snapshotting tool
"""

from typing import Sequence, Union, Optional
import subprocess
import tempfile
import datetime
import argparse
from itertools import chain


def _run(command: Union[str, Sequence[str]], **kwargs) -> str:
    """
    Wrapper for `subprocess.run()`:

    - Accepts args as either a list of strings or space-delimited string
    - Captures and returns stdout

    Args:
        command: A list of strings or a space-delimited string
        **kwargs: Passed to `subprocess.run()`

    Returns:
        Captured stdout
    """
    args: Sequence[str]
    if isinstance(command, str):
        args = command.split()
    else:
        args = command
    result = subprocess.run(args, stdout=subprocess.PIPE, **kwargs)
    return result.stdout.decode().strip()


def get_latest_commit(short: bool = True, cwd: Optional[str] = None) -> str:
    """
    Get the most recent commit's hash.
    This includes non-lethe commits.
    """
    fmt = 'h' if short else 'H'
    return _run(f'git log --all -1 --format=%{fmt}', cwd=cwd)


def shorten_hash(sha: str, cwd: Optional[str] = None) -> str:
    """
    Get the short version of a hash
    """
    return _run(f'git rev-parse --short {sha}', cwd=cwd)


def get_root(cwd: Optional[str] = None) -> str:
    """
    Get the root directory of a git repository
    """
    root = _run('git rev-parse --show-toplevel', cwd=cwd)
    if not root:
        raise Exception('Must be run from inside git repository!')
    return root


def get_obj(ref: str, cwd: Optional[str] = None) -> str:
    """
    Transform a ref into its corresponding hash using git-rev-parse
    """
    sha = _run('git rev-parse --quiet --verify'.split() + [ref], cwd=cwd)
    return sha


def get_commit(ref: str, cwd: Optional[str] = None) -> str:
    """
    Transform a ref to a commit into its corresponding hash using git-rev-parse
    """
    return get_obj(ref, cwd=cwd)


def get_tree(ref: str, cwd: Optional[str] = None) -> str:
    """
    Take a ref to a commit, and return the hash of the tree it points to
    """
    return get_obj(ref + ':', cwd=cwd)


def commit_tree(tree: str,
                parents: Sequence[str],
                message: Optional[str] = None,
                cwd: Optional[str] = None,
                ) -> str:
    """
    Create a commit pointing to the given tree, with the specified parent commits and message.
    Return the hash of the created commit.
    """
    if message is None:
        message = 'snapshot ' + str(datetime.datetime.now())

    pargs = list(chain.from_iterable(('-p', p) for p in parents))
    commit = _run(['git', 'commit-tree', tree, *pargs, '-m', message], cwd=cwd)   # Create commit
    return commit


def update_ref(target_ref: str,
               target_commit: str,
               old_commit: Optional[str] = None,
               *,
               message: str = 'new snapshot',
               cwd: Optional[str] = None,
               ) -> str:
    """
    Update `target_ref` to point to `target_commit`, optionally verifying that
        it points `old_commit` before the update.
    Returns the resulting ref.
    """
    cmd = ['git', 'update-ref', '-m', message, target_ref, target_commit]
    if old_commit is not None:
        cmd.append(old_commit)
    result_ref = _run(cmd, cwd=cwd)
    return result_ref


def push_ref(remote: str = 'origin',
             target_ref: str = 'refs/lethe/LATEST',
             remote_ref: Optional[str] = None,
             *,
             cwd: Optional[str] = None,
             ) -> str:
    """
    Push `target_ref` to `remote` as `remote_ref`.
    By default, `remote_ref` will be the same as `target_ref`.

    Args:
        remote: git remote to push to (default 'origin')
        target_ref: ref to push (default 'refs/lethe/LATEST')
        remote_ref: ref to push to (default same as `target_ref`)
        cwd: Repository directory. Default is current working directory.

    Returns:
        git command stdout
    """
    if remote_ref is None:
        remote_ref = target_ref
    return _run(['git', 'push', '--force', remote, target_ref + ':' + remote_ref], cwd=cwd)


def fetch_ref(remote: str = 'origin',
              remote_ref: str = 'refs/lethe/LATEST',
              target_ref: Optional[str] = None,
              *,
              cwd: Optional[str] = None,
              ) -> str:
    """
    Fetch `remote_ref` from `remote` as `target_ref`.
    By default, `target_ref` will be the same as `remote_ref`.

    Args:
        remote: git remote to push to (default 'origin')
        remote_ref: ref to fetch from (default 'refs/lethe/LATEST')
        target_ref: ref to fetch to (default same as `remote_ref`)
        cwd: Repository directory. Default is current working directory.

    Returns:
        git command stdout
    """
    if target_ref is None:
        target_ref = remote_ref
    return _run(['git', 'fetch', '--force', remote, remote_ref + ':' + target_ref], cwd=cwd)


def deref_symref(ref: str,
                 *,
                 cwd: Optional[str] = None,
                 ) -> str:
    """
    Dereference a symbolic ref
    """
    return _run(['git', 'symbolic-ref', '--quiet', ref], cwd=cwd)


def find_merge_base(commits: Sequence[str],
                    *,
                    cwd: Optional[str] = None,
                    ) -> str:
    """
    Find the "best common ancestor" commit.

    Args:
        commits: Collection of commits to find the best common ancestor for
        cwd: Repository directory. Default is current working directory.

    Returns:
        Hash of the best common ancestor commit
    """
    if len(commits) == 0:
        raise Exception('Called find_merge_base with no commits!')

    if len(commits) == 1:
        return commits[0]

    base = _run(['git', 'merge-base', *commits], cwd=cwd)
    return base


def snap_tree(*, cwd: Optional[str] = None) -> str:
    """
    Create a new tree, consisting of all non-ignored files in the repository.
    Return the hash of the tree.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        env = {'GIT_INDEX_FILE': tmp_dir + '/git-snapshot-index'}

        # TODO: Maybe need cwd=get_root(cwd) here?
        _run('git add --all', env=env, cwd=cwd)
        tree = _run('git write-tree', env=env, cwd=cwd)
    return tree


def snap_ref(parent_refs: Sequence[str],
             target_refs: Sequence[str],
             message: Optional[str] = None,
             *,
             cwd: Optional[str] = None,
             ) -> str:
    """
    `message` is used as the commit message.
    """
    new_tree = snap_tree(cwd=cwd)
    parent_commits = [c for c in [get_commit(p, cwd=cwd) for p in parent_refs] if c]
    old_commits = [get_commit(t, cwd=cwd) for t in target_refs]

    commit = commit_tree(new_tree, set(parent_commits), message, cwd=cwd)

    for target_ref, old_commit in zip(target_refs, old_commits):
        # update ref to point to commit, or create new ref
        old_or_none = old_commit if old_commit else None
        update_ref(target_ref, commit, old_commit=old_or_none, cwd=cwd)

    return commit


def snap(parent_refs: Optional[Sequence[str]] = None,
         target_refs: Optional[Sequence[str]] = None,
         message: Optional[str] = None,
         *,
         cwd: Optional[str] = None,
         ) -> str:
    """
    Create a new commit, containing all non-ignored files.

    Args:
        parent_refs: Refs in this list are set as parents of the new commit.
            If any symbolic refs are included, the underlying refs they point
            to are also added to `parent_refs`. Defaults to `['HEAD']`.
        target_refs: Refs in this list will be updated to point to the new commit.
            Default is
                - 'refs/lethe/LATEST', and
                - 'refs/lethe/path/to/ref/LATEST' and
                  'refs/lethe/path/to/ref/snap_2020-12-20_18.21.14.281876'
                  for each parent_ref of the form 'refs/path/to/ref'.
                  Symbolic refs are dereferenced, so a parent_ref of 'master'
                  will results in the creation/overwrite of
                  'refs/lethe/heads/master/LATEST'
            Note that 'refs/lethe/LATEST' must be specified explicitly if the default
            is overridden
        message: The commit message. Default is a simple note containing the current
            date/time.
        cwd: Path to the repository. Default is the current working directory.

    Returns:
        The hash for the new commit.
    """
    if parent_refs is None:
        parent_refs = ['HEAD']
    else:
        parent_refs = list(parent_refs)

    parent_refs += [r for r in [deref_symref(s, cwd=cwd) for s in parent_refs] if r]

    date_str = str(datetime.datetime.now())
    date_ref = date_str.replace(' ', '_').replace(':', '.')

    if target_refs is None:
        target_refs = ['refs/lethe/LATEST']
        for pp in parent_refs:
            if not pp.startswith('refs/'):
                continue
            target_base = 'refs/lethe/' + pp[len('refs/'):]
            target_refs += [target_base + '/LATEST',
                            target_base + '/' + date_ref]

            # Auto-migrate old commits to work with the new scheme
            old_base_commit = get_commit(target_base, cwd=cwd)
            if old_base_commit:
                print(f'Migrating {target_base} to new naming scheme ({target_base}/LEGACY)...')
                print(f'You may also want to delete refs/lethe/HEAD with `git update-ref -d refs/lethe/HEAD`')
                _run('git update-ref -d ' + target_base)
                update_ref(target_base + '/LEGACY', old_base_commit,
                           message='last commit using old refs/lethe/branchname approach')


    if message is None:
        message = 'snapshot ' + date_str

    commit = snap_ref(parent_refs, target_refs, message=message, cwd=cwd)
    return commit
