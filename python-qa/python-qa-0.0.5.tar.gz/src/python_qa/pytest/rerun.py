import os

import git
import pytest


class PyTestReRunPlugin:
    diff = []

    def __init__(self, main_branch, diff_branch):
        self.main_branch = main_branch
        self.diff_branch = diff_branch
        self.repo = git.Repo(os.getcwd())
        self.repo.git.fetch()
        self.collect_diff()

    def collect_diff(self):
        diff_branch = (
            self.diff_branch
            if self.diff_branch != "current" else self.repo.active_branch.name
        )
        diff = self.repo.git.diff(
            self.main_branch + '..' + diff_branch, name_only=True
        ).split("\n")
        self.diff = [os.path.abspath(i) for i in diff]
        print(diff)

    @pytest.hookimpl(tryfirst=True)
    def pytest_ignore_collect(self, path, config):
        if os.path.isdir(path):
            return False
        elif not self.diff:
            return False
        return path not in self.diff
