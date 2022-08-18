import asyncio
import logging
import os
import pathlib
import sys
from unittest import mock

import _pytest.python as pythtest
import pop.hub
import pytest

import pytest_pop.mods.testing as testing

log = logging.getLogger("pytest_pop.plugin")


def pytest_sessionstart(session: pytest.Session):
    root = pathlib.Path(session.config.rootdir)
    CODE_DIR = str(root)
    if CODE_DIR in sys.path:
        sys.path.remove(CODE_DIR)
    sys.path.insert(0, CODE_DIR)


@pytest.fixture(autouse=True, scope="session", name="hub")
def session_hub():
    """
    Create a base hub that is scoped for session, you should redefine it in your own conftest.py
    to be scoped for modules or functions
    """
    hub = pop.hub.Hub()

    # Set up the rudimentary logger
    hub.pop.sub.add(dyne_name="log")

    yield hub


@pytest.fixture()
def event_loop(hub, event_loop):
    hub.pop.loop.CURRENT_LOOP = event_loop

    yield event_loop

    event_loop.close()


@pytest.fixture(autouse=True, scope="session")
def setup_session():
    pass


@pytest.fixture(autouse=True, scope="session")
def teardown_session():
    pass


@pytest.fixture(autouse=True, scope="module")
def setup_module():
    pass


@pytest.fixture(autouse=True, scope="module")
def teardown_module():
    pass


@pytest.fixture(autouse=True, scope="function")
def setup_function():
    pass


@pytest.fixture(autouse=True, scope="function")
def teardown_function():
    pass


@pytest.fixture(scope="function")
def mock_hub(hub):
    m_hub = hub.pop.testing.mock_hub()
    m_hub.OPT = mock.MagicMock()
    m_hub.SUBPARSER = mock.MagicMock()
    yield m_hub


@pytest.fixture(scope="function")
def contract_hub(hub):
    yield testing.ContractHub(hub)


@pytest.fixture(scope="function")
def lazy_hub(hub):
    yield testing._LazyPop(hub)


@pytest.fixture(scope="function")
def mock_attr_hub(hub):
    yield hub.pop.testing.mock_attr_hub()


@pytest.fixture(scope="function")
def fn_hub(hub):
    yield hub.pop.testing.fn_hub()


def pytest_collection_modifyitems(config, items):
    # Mark all unmarked async tests
    for item in items:
        if hasattr(item.obj, "hypothesis"):
            test_func = item.obj.hypothesis.inner_test
        else:
            test_func = item.obj
        if not item.own_markers and asyncio.iscoroutinefunction(test_func):
            item.add_marker(pytest.mark.asyncio())


def pytest_runtest_protocol(item: pythtest.Function, nextitem: pythtest.Function):
    """
    implements the runtest_setup/call/teardown protocol for
    the given test item, including capturing exceptions and calling
    reporting hooks.
    """
    log.debug(f">>>>> START >>>>> {item.name}")


def pytest_runtest_teardown(item: pythtest.Function):
    """
    called after ``pytest_runtest_call``
    """
    log.debug(f"<<<<< END <<<<<<< {item.name}")


@pytest.fixture(scope="session", autouse=True)
def os_sleep_secs():
    if "CI_RUN" in os.environ:
        return 1.75
    return 0.5
