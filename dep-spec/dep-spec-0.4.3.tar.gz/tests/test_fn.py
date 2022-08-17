"""Test fn."""

from typing import Dict

import pytest

from spec import fn

NAME = 'ANY'
ANY = f'{NAME}_KEY'
PREFIX = 'PREFIXED'
ANY_PREFIXED = f'{PREFIX}_{ANY}'

APP_PLUGIN_ALIAS = 'tickets'
PLUGIN_NAME = 'mongo'
PLUGIN_PARAM_URI_NAME = 'uri'
PLUGIN_PARAM_URI_VALUE = 'any.db.uri'

PLUGIN_PARAM_POOL_SIZE_NAME = 'pool_size'
PLUGIN_PARAM_POOL_SIZE_VALUE = '10'


@pytest.fixture
def no_prefixed(monkeypatch):
    """Mock plugin aliased params."""
    monkeypatch.setenv(ANY, '1')
    yield
    monkeypatch.delenv(ANY, raising=False)


@pytest.fixture
def prefixed(monkeypatch):
    """Mock plugin aliased params."""
    monkeypatch.setenv(ANY_PREFIXED, '1')
    yield
    monkeypatch.delenv(ANY_PREFIXED, raising=False)


@pytest.fixture
def plugin_options(monkeypatch) -> Dict:
    """Plugin options."""
    name = PLUGIN_NAME.upper()
    app_plugin_alias = APP_PLUGIN_ALIAS.upper()

    param_uri = 'PLUGIN_{name}_{alias}_{param}'.format(
        name=name,
        alias=app_plugin_alias,
        param=PLUGIN_PARAM_URI_NAME.upper(),
    )

    param_pool = 'PLUGIN_{name}_{alias}_{param}'.format(
        name=name,
        alias=app_plugin_alias,
        param=PLUGIN_PARAM_POOL_SIZE_NAME.upper(),
    )

    options = {
        param_uri: PLUGIN_PARAM_URI_VALUE,
        param_pool: PLUGIN_PARAM_POOL_SIZE_VALUE,
    }

    for set_name, set_value in options.items():
        monkeypatch.setenv(set_name, set_value)

    yield options

    for del_name, del_value in options.items():
        monkeypatch.delenv(del_name)


def test_env_alias_not_exist():
    """Check env aliased options if exists."""
    assert not fn.alias_option_exist(NAME)


def test_env_alias_exist(no_prefixed):
    """Check env aliased options if exists."""
    assert fn.alias_option_exist(NAME)


def test_env_alias_prefix_not_exist():
    """Check env aliased options if exists."""
    assert not fn.alias_option_exist(NAME, prefix=PREFIX)


def test_env_alias_prefix_exist(prefixed):
    """Check env aliased options if exists."""
    assert fn.alias_option_exist(NAME, prefix=PREFIX)


def test_alias_group(plugin_options):
    """Test read env alias plugin."""

    assert fn.alias_plugin_options(
        alias=APP_PLUGIN_ALIAS,
        plugin=PLUGIN_NAME
    ) == {
        PLUGIN_PARAM_URI_NAME.lower(): PLUGIN_PARAM_URI_VALUE,
        PLUGIN_PARAM_POOL_SIZE_NAME.lower(): PLUGIN_PARAM_POOL_SIZE_VALUE,
    }


def test_alias_group_empty():
    """Test read env alias plugin."""

    assert fn.alias_plugin_options(
        alias=APP_PLUGIN_ALIAS,
        plugin=PLUGIN_NAME,
    ) == dict()
