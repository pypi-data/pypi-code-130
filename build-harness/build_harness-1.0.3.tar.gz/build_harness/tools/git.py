#
#  Copyright (c) 2021 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.
#

"""Manage git command options."""

import dataclasses
import logging
import os
import pathlib
import re
import shutil
import typing

import git  # type: ignore
import git.objects  # type: ignore

log = logging.getLogger(__name__)

DEFAULT_DEFAULT_BRANCH_NAME = "master"


class GitNotFoundError(Exception):
    """Git executable not found error."""


class GitRepoError(Exception):
    """Git repository error."""


class TagDataError(Exception):
    """Tag, offset extraction error."""


def validate_git(optional_git: typing.Optional[str]) -> None:
    """
    Validate that git is installed or the user has provided a valid git path.

    Args:
        optional_git: Path to git executable.

    Raises:
        GitNotFoundError: If git executable not found.
    """
    system_git = shutil.which("git")
    if optional_git:
        system_git = optional_git

    if not system_git:
        raise GitNotFoundError("Git not available on users PATH")
    if not os.path.exists(system_git):
        raise GitNotFoundError(
            "User specified git invalid, {0}".format(system_git)
        )


@dataclasses.dataclass
class TagData:
    """Tag, offset data extracted from git describe."""

    tag: str
    offset: typing.Optional[str] = None


def _is_commit_tagged(commit_sha: git.objects.Commit, repo: git.Repo) -> bool:
    """Verify that the specified commit is not tagged."""
    tag_commits = [x.commit for x in repo.tags]
    return any(commit_sha == x for x in tag_commits)


def _parse_describe(describe_output: str) -> TagData:
    """Extract tag, offset data from git describe output."""
    match = re.search(r"(?P<tag>.+?)(-(?P<offset>\d+)-(.+))?$", describe_output)

    if match:
        value = TagData(tag=match.group("tag"), offset=match.group("offset"))
    else:
        raise TagDataError(
            "Unable to match git describe output, {0}".format(describe_output)
        )

    return value


def get_tag_data(
    repo_path: pathlib.Path,
    default_branch_name: typing.Optional[str] = None,
) -> TagData:
    """
    Acquire tag, offset data for release id construction.

    Assumes that the repo has already been set to the required HEAD state.

    Args:
        repo_path: Path to git repository.
        default_branch_name: Name of the default branch in the repo.

    Returns:
        Parsed tag data, if possible.
    Raises:
        GitRepoError: If unable to parse PEP-440 compliant tag.
    """
    try:
        this_repo = git.Repo(str(repo_path))
        try:
            # Start with the nearest historical tag.
            result = this_repo.git.describe("--first-parent", "--tags")

            # If HEAD is dryrun tagged then this is a dryrun so use that tag
            # (ie. treat it as a release).
            if (not _is_commit_tagged(this_repo.head.commit, this_repo)) and (
                re.search(r"\+dryrun", result) is not None
            ):
                # It's a dryrun tag, so search again excluding dryrun tags.
                result = this_repo.git.describe(
                    "--first-parent",
                    "--tags",
                    "--exclude",
                    "*+dryrun*",
                )
            tag_data = _parse_describe(result)
        except git.GitCommandError as e:
            log.debug("handling GitCommandError, {0}".format(str(e)))
            # NOTE: the fallback here is to assume the active branch is the
            #       default branch. there might be unexpected side effects of
            #       this choice.
            this_branch = (
                default_branch_name
                if default_branch_name
                else this_repo.active_branch.name
            )
            number_commits = len(list(this_repo.iter_commits(this_branch)))
            tag_data = TagData(tag="0.0.0", offset=str(number_commits))

    except TagDataError as e:
        log.debug("handling TagDataError, {0}".format(str(e)))
        # extreme fallback that is not expected to happen in practice
        # use a PEP-440 local identifier to prevent publishing because at this
        # point that is almost certainly not desirable
        tag_data = TagData(tag="0.0.0", offset=None)
    except git.InvalidGitRepositoryError as e:
        log.debug("handling git.InvalidGitRepositoryError, {0}".format(str(e)))
        raise GitRepoError(
            "Invalid git repository, {0}".format(repo_path)
        ) from e

    return tag_data
