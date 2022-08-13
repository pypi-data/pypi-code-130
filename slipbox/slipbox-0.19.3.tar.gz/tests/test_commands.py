"""Test commands.py."""

from configparser import ConfigParser
from pathlib import Path
import pytest

from slipbox import commands
from slipbox.app import App, RootlessApp, startup
from slipbox.build import build
from slipbox.dependencies import check_requirements


def test_show_info_missing_note(
    app: App,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """show_info should print error message and exit with error code."""
    app.args = {"note_id": 0}

    with pytest.raises(SystemExit) as system_exit:
        commands.show_info(app)
        stdout, stderr = capsys.readouterr()
        assert not stdout
        assert stderr

    assert system_exit.value.code != 0


@pytest.mark.skipif(not check_requirements(startup({})),
                    reason="missing requirements")
def test_show_info_in_stdout(
    app: App,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """show_info should output note info in stdout."""
    Path("test.md").write_text("# 0 Test\n\nTest note.")

    build(app)
    app.args = {"note_id": 0}
    commands.show_info(app)
    stdout, stderr = capsys.readouterr()
    assert stdout
    assert not stderr


def test_init_creates_config_file(app_without_root: RootlessApp) -> None:
    """init must create .slipbox/config.cfg."""
    app = app_without_root
    commands.init(app)
    assert app.root is not None

    hidden = app.root/".slipbox"
    assert hidden.is_dir()
    assert hidden.joinpath("config.cfg").is_file()


def test_init_quiet(
    app_without_root: App,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """init must not print anything in quiet mode."""
    app = app_without_root
    app.args["quiet"] = True
    commands.init(app)
    stdout, stderr = capsys.readouterr()
    assert not stdout
    assert not stderr


def test_init_root(app_without_root: RootlessApp) -> None:
    """init must set app.root."""
    app = app_without_root
    assert app.root is None
    commands.init(app)
    assert app.root is not None


def test_init_patterns(app_without_root: RootlessApp) -> None:
    """.slipbox/config.cfg must contain some glob patterns."""
    app = app_without_root
    commands.init(app)
    assert app.root is not None
    hidden = app.root/".slipbox"

    parser = ConfigParser()
    parser.read(hidden/"config.cfg")

    assert parser.getboolean("note-patterns", "*.md")
    assert parser.getboolean("note-patterns", "*.rst")
