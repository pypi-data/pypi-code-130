from python_qa.pytest.rerun import PyTestReRunPlugin


def pytest_addoption(parser):
    parser.addoption(
        "--only-changed", action="store_true", default=False, help=""
    )
    parser.addoption(
        "--rerun-main-branch", action="store", default=None,
        help="Branch which will be used as main in diff\n"
             "(Default: origin/master)"
    )
    parser.addoption(
        "--rerun-diff-branch", action="store", default=None,
        help="Branch which will be used as diff for the main\n"
             "(Default: <current>)"
    )
    parser.addini(
        "rerun-main-branch",
        "Branch which will be used as main in diff",
        default=None,
    )
    parser.addini(
        "rerun-diff-branch",
        "Branch which will be used as diff for the main",
        default=None,
    )


def pytest_configure(config):
    if config.getoption("--only-changed"):
        main_branch = (
                config.getoption("--rerun-main-branch")
                or config.getini("rerun-main-branch")
                or "origin/master"
        )
        diff_branch = (
                config.getoption("--rerun-diff-branch")
                or config.getini("rerun-diff-branch")
                or "current"
        )
        config.pluginmanager.register(
            PyTestReRunPlugin(
                main_branch=main_branch,
                diff_branch=diff_branch
            ),
            name="pytest-rerun-instance"
        )
