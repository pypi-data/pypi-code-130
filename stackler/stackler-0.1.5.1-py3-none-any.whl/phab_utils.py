"""
Phabricator related utils for Stackler
"""

import os
import re
import json
import sys

from phabricator import Phabricator
from git import Commit, Repo

PHABRICATOR_CONFIG_PATH = r".arcconfig"
PHBARICATOR_URI_KEY = r"phabricator.uri"

STATUS_CODE_ACCEPTED = 2


def _get_phab_uri() -> str:
    try:
        with open(PHABRICATOR_CONFIG_PATH, "r", encoding="utf-8") as arc_cfg_file:
            data = json.load(arc_cfg_file)
            return data[PHBARICATOR_URI_KEY]
    except FileNotFoundError:
        print(".arcconfig not found. Are you on the root directory of the repo?", file=sys.stderr)
        sys.exit(1)


P = Phabricator()
DIFF_REGEX = rf"(?<=Differential Revision: {_get_phab_uri()})D\d+"


def has_diff_attached(commit_id: str = ""):
    """Checks if the commit has a diff attached by checking the commit msg"""
    return re.search(DIFF_REGEX, _get_commit(commit_id=commit_id).message)


def get_diff_id(commit_id: str = "", pure_id: bool = False) -> str:
    """Gets diff id like Dxxxxxx from a commit, HEAD if not specified"""
    diff_id = re.findall(DIFF_REGEX, _get_commit(commit_id=commit_id).message)[-1]
    return diff_id[(1 if pure_id else 0):]


def add_parent_to_diff(diff_id: str, parent_diff_id: str):
    """Adds the parent diff as the parent diff for the given diff_id"""
    parent_phid = _get_phid_from_diff_id(parent_diff_id)
    P.differential.revision.edit(transactions=[{"type": "parents.add", "value": [
                                 parent_phid]}, ], objectIdentifier=diff_id)


_cache: dict[Commit: dict[str, str]] = {}


def fetch_matadata_from_commits(*commits: Commit):
    """
    Gets matadata from phabricator given commits
    {
        Commit: {
            {
                "id": "xxxxxx",
                "phid": "PHID-xxxxxxxxxxxxxxxxxxxxxxxxx",
                "title": "xxxxxxxxxx",
                "uri": "https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "dateCreated": "16608xxxxx",
                "dateModified": "166080xxxx",
                "authorPHID": "PHID-USER-xxxxxxxxxxxxxxxxxxxx",
                "status": "x",
                "statusName": "xxxxxx",
                "properties": {
                "draft.broadcast": true,
                "lines.added": 1,
                "lines.removed": 0,
                "buildables": {
                    "PHID-HMBB-xxxxxxxxxxxxxxxxxxxx": {
                    "status": "passed"
                    }
                },
                "wasAcceptedBeforeClose": false
                },
                "branch": null,
                "summary": "xxxxxxxxxxxx",
                "testPlan": "xxxxxxxxxx",
                "lineCount": "1",
                "activeDiffPHID": "PHID-DIFF-xxxxxxxxxxxxxxxxxxxx",
                "diffs": [
                "xxxxxx",
                "xxxxxx"
                ],
                "commits": [
                "PHID-CMIT-xxxxxxxxxxxxxxxxxxxx"
                ],
                "reviewers": [],
                "ccs": [],
                "hashes": [
                [
                    "gtcm",
                    "cf7afb5011200ecc3xxxxxxxxxxxxxxxxxxxxxxx"
                ],
                [
                    "gttr",
                    "59c3336f45f0f0a072exxxxxxxxxxxxxxxxxxxxx"
                ]
                ],
                "auxiliary": {
                "phabricator:projects": [],
                "phabricator:depends-on": [
                    "PHID-DREV-xxxxxxxxxxxxxxxxxxxx"
                ]
                },
                "repositoryPHID": "PHID-REPO-xxxxxxxxxxxxxxxxxxxx",
                "sourcePath": null
            }
        },
        Commit: {
            ...
        }
    }

    """
    diff_ids_to_cmts = {get_diff_id(cmt, pure_id=True): cmt
                        for cmt in commits
                        if has_diff_attached(cmt)}
    if diff_ids_to_cmts:
        raw_matadata = P.differential.query(ids=list(diff_ids_to_cmts.keys()))
        _cache.update({diff_ids_to_cmts[m['id']]: dict(m) for m in raw_matadata})


def get_matadata_from_commit(commit: Commit) -> dict[str, str]:
    """
    Returns the matadata from a given commit.
    """
    assert has_diff_attached(commit), "The commit must have a diff attached."
    if commit not in _cache:
        fetch_matadata_from_commits(commit)
    return _cache[commit]


def are_commits_all_accepted(*commits: Commit):
    """Returns if all the commits are accepted."""
    return all(
        has_diff_attached(cmt)
        and int(get_matadata_from_commit(cmt)['status']) == STATUS_CODE_ACCEPTED
        for cmt in commits)


def _get_micro_matadata_from_diff_id(*diff_ids: str) -> dict[str, str]:
    """
    Gets micro matadata from phabricator given a diff id
    {
        "Dxxxxxx": {
            "phid": "PHID-xxxx-xxxxxxxxxxxxxxxxxxxx",
            "uri": "https://xxxxxxxxxxxxxxxxxxxxxxxxxxx/Dxxxxxx",
            "typeName": "Differential Revision",
            "type": "xxxx",
            "name": "Dxxxxxx",
            "fullName": "xxxxxxxxxxxxxxxxxxxxxx",
            "status": "xxxx"
        },
        "Dxxxxxx": {
            ...
        }
    }
    """
    return P.phid.lookup(names=diff_ids)


def _get_phid_from_diff_id(diff_id: str) -> str:
    """Gets PHID from phabricator given a diff id"""
    return _get_micro_matadata_from_diff_id(diff_id)[diff_id]["phid"]


def _get_commit(commit_id: str = "") -> Commit:
    """Gets commit by id, HEAD if not specified"""
    repo = Repo(os.getcwd())
    cmt = repo.commit(commit_id) if commit_id else repo.head.commit
    return cmt
