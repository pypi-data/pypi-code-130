"""
Main Stackler Script
"""

from datetime import datetime
import subprocess
import sys

import click
from git import Repo
import typer

from stackler import display_utils
from stackler import phab_utils
from stackler import git_utils
from stackler.git_utils import REPO_PATH, BASE_TAG

app = typer.Typer()


arg_sha = typer.Argument(..., help="The SHA to the commit")

option_base = typer.Option(
    BASE_TAG,
    "--base", "-b",
    help='The base commit of the stack')
option_update_message = typer.Option(
    '',
    "--update-message", "-m",
    help='The message for updating a diff')
option_dry_run = typer.Option(
    False,
    "--dry-run", "-n",
    help='Print which commits are going to be submitted, but doesn\'t submit anything')
option_interactive_submit = typer.Option(
    False,
    "--interactive-submit", "-i",
    help='Use this flag if you want to manually enter the diff summary for new commits')


@app.command()
def submit(
        base: str = option_base,
        interactive_submit: bool = option_interactive_submit,
        update_message: str = option_update_message,
        dry_run: bool = option_dry_run,
        debug_dry_run: bool = False):
    """
    Submit a stack of commits separately.
    Use -b to specify a base if you aren't working on <develop>.
    """
    _precheck(base)
    _submit(base,
            interactive_submit,
            update_message,
            dry_run,
            debug_dry_run,
            prompt_dry_run=False)


def _submit(base: str,
            interactive_submit: bool,
            update_message: str,
            dry_run: bool,
            debug_dry_run: bool,
            prompt_dry_run=False):

    # do an internal dry run to show the prompt
    if not dry_run and not debug_dry_run and not prompt_dry_run:
        print("By continuing, this script will:")
        _submit(base,
                interactive_submit,
                update_message,
                dry_run,
                debug_dry_run,
                prompt_dry_run=True)
        if not click.confirm('Do you want to continue?', default=True):
            display_utils.print_error('Aborted')
            return

    # To submit a stack, a few things need to happen:
    # 1. find the base commit, which will remain unchanged for the entirety of
    # the operation.
    # 2. go through the stack of commits one by one via checkout:
    #     a. diff it out, get a modified commit
    #     b. connect diff with the previous one
    #     c. checkout the tip of the stack, rebase it onto the lastly modified
    #     commit
    # 3. move HEAD to the new tip

    repo = Repo(REPO_PATH)
    current_branch = repo.active_branch
    base_commit = repo.commit(base)
    prev_commits = [repo.head.commit]
    for prev_commit in repo.head.commit.traverse():
        if prev_commit == base_commit:
            break
        prev_commits.append(prev_commit)

    # 1. find the base commit
    current_commit = prev_commits[-1]
    if base_commit == current_commit:
        print("No commits to submit")
        return

    # 2. go through the stack of commits
    prev_commit = base_commit
    prev_diff_id = ''
    current_diff_id = ''
    has_updates = False
    for i in range(len(prev_commits)):
        # sanity check:
        # Base - A - B - C - D
        # len(prev_commits) = 4
        # i goes from 0 to 3
        # to go to A, we need HEAD^3 (4 - 1)
        # hence `len(prev_commits) - i - 1`
        # HEAD^x now has x going from 3 to 0; current_commit from A to D
        current_commit = repo.commit(f'HEAD~{len(prev_commits) - i - 1}')

        repo.git.checkout(current_commit)
        is_updating = phab_utils.has_diff_attached()
        if is_updating:
            current_diff_id = phab_utils.get_diff_id()
            has_updates = True

        # show msgs
        if is_updating:
            display_utils.print_update_msg(
                current_commit, current_diff_id, update_message)
        else:
            display_utils.print_submit_msg(current_commit, prev_commit)

        # 2a. diff it out
        if not prompt_dry_run and not dry_run and not debug_dry_run:
            arc_args = ["arc", "diff", prev_commit.hexsha]
            if is_updating and update_message:
                arc_args.append('-m')
                arc_args.append(update_message)
            if (not is_updating) and (not interactive_submit):
                arc_args.append("--verbatim")
            try:
                subprocess.run(arc_args, check=True)
            except subprocess.CalledProcessError:
                display_utils.print_warning(
                    "arc sumbit failed. Please start over."
                )
                print(
                    f"The command ran: {' '.join(arc_args)}"
                )
                repo.git.checkout(current_branch)
                sys.exit(1)

            # 2b. connect the diff with previous one
            current_diff_id = phab_utils.get_diff_id()
            if not is_updating and prev_diff_id:
                phab_utils.add_parent_to_diff(current_diff_id, prev_diff_id)
            prev_diff_id = current_diff_id

        elif debug_dry_run:
            subprocess.run(
                f"git commit --amend -m '{repo.head.commit.message}updated at {datetime.now()}'",
                shell=True,
                check=True)

        # 2c. restack
        prev_commit = repo.head.commit
        repo.git.checkout(current_branch)
        repo.git.rebase(prev_commit.hexsha)

    if prompt_dry_run and has_updates and not update_message:
        display_utils.print_warning(
            "You have not specified an update message. " +
            "Make sure you manually add one for all the diff updates, or the operation would fail."
        )

    # 3. move HEAD to new tip
    # already performed


@ app.command()
def edit(sha: str = arg_sha,
         base: str = option_base):
    """
    Allows you to edit a commit within a stack easily.
    This is basically just a wrapper for `git rebase sha^`)
    Use -b to specify a base if you aren't working on <develop>.
    """
    _precheck(base)
    if not git_utils.is_commit_in_stack(sha, tip='HEAD', base=base):
        display_utils.print_error(
            f"The commit <{sha[:8]}> isn't in the stack.")
        print("Stackler only supports editing a commit in the working stack:")
        show(base)
        sys.exit(1)

    editor_cmd = "sed -i -re '1s/pick/e/'"
    git_cmd = f"git rebase -i {sha}^"
    print(f"GIT_SEQUENCE_EDITOR={editor_cmd} {git_cmd}")
    subprocess.run(
        f"GIT_SEQUENCE_EDITOR=\"{editor_cmd}\" {git_cmd}", shell=True, check=True)


@app.command()
def show(base: str = option_base):
    """
    Prints the stack.
    """
    _precheck(base)
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits(f"{base}..HEAD"))
    if not commits:
        display_utils.print_warning('No commits in the stack.')
    else:
        phab_utils.fetch_matadata_from_commits(*commits)
    for i, commit in enumerate(commits):
        print(('| ' if i > 0 else '↑ ') + display_utils.commit_summary(commit, short=False))
    display_utils.print_base(base, repo.commit(f"{base}"))


@app.command()
def land(base: str = option_base, bypass_accepted_check: bool = False):
    """
    Lands the stack. This command does prechecks to ensure the land is successful.
    """
    _precheck(base)
    repo = Repo(REPO_PATH)
    commits = list(repo.iter_commits(f"{base}..HEAD"))
    if not phab_utils.are_commits_all_accepted(*commits) and not bypass_accepted_check:
        display_utils.print_error("All the diffs must be accepted before you can land.")
        sys.exit(0)
    print("Before landing, this script needs to pull and rebase.")
    print("Right now, Stackler only supports landing onto the git upstream, "
          + "so the rebase command about to run is `git pull --rebase`. "
          + "You could run into merge conflicts.'")
    if not click.confirm('Continue?', default=True):
        display_utils.print_error('Aborted.')
        sys.exit(1)
    else:
        print('Starting pulling and rebasing.')

    try:
        subprocess.run(['git', 'pull', '--rebase'], check=True)
    except subprocess.CalledProcessError:
        display_utils.print_warning(
            'Looks like something hit an error. Mostly likely a merge conflict.')
        print('If that\'s the case, You may resolve it and try again, starting with `git status`.')
        sys.exit(1)

    current_branch = repo.active_branch
    print('Starting landing.')
    arc_args = ['arc', 'land']
    try:
        subprocess.run(arc_args, check=True)
    except subprocess.CalledProcessError:
        display_utils.print_warning(
            "arc land failed. Please start over."
        )
        print(
            f"The command ran: {' '.join(arc_args)}"
        )
        sys.exit(1)

    # if landing a branchless stack, the repo is left detached, this hack resets it
    try:
        repo.active_branch
    except TypeError:
        repo.git.checkout(current_branch)


def _precheck(base: str):
    """
    Exits the command if precheck fails.
    Precheck checks for dirty repo, untracked files, and detached head.
    """
    repo = Repo(REPO_PATH)

    if not git_utils.get_commit_safe(base):
        display_utils.print_error(
            f"The base {base} doesn't exist. Please double check the SHA.")
        sys.exit(1)

    if git_utils.is_detached():
        display_utils.print_error(
            "The head is detached. Please attach it and try again.")
        display_utils.print_warning(
            "Usually the command to do so is `git checkout develop`")
        sys.exit(1)

    if git_utils.is_dirty():
        display_utils.print_error("The repo is dirty.")
        display_utils.print_warning("Please commit or discard all your changes.")
        sys.exit(1)

    if git_utils.is_unstaged():
        display_utils.print_error("There are untracked files:")
        file_str = '\n'.join(repo.untracked_files)
        print(file_str)
        display_utils.print_warning(
            "Please commit them by `git commit -am  <commit message>`")
        sys.exit(1)


@ app.callback()
def callback():
    """Stackler makes working with stacks easier."""
    # This makes Typer treat submit as an explict command
