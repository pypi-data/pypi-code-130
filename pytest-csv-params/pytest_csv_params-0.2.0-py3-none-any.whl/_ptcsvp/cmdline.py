"""
Command Line Options
"""
from _pytest.config.argparsing import Parser

HELP_TEXT = "set base dir for getting CSV data files from"


def pytest_addoption(parser: Parser, plugin_name: str = "csv-params") -> None:
    """
    Add Command Line Arguments for pytest execution
    """

    group = parser.getgroup(plugin_name)
    group.addoption(
        f"--{plugin_name}-base-dir",
        action="store",
        type=str,
        default=None,
        required=False,
        help=HELP_TEXT,
    )
