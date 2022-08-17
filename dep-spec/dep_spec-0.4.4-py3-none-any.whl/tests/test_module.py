"""Test modules."""

import asyncio
import logging
import pytest

from asgi_lifespan import LifespanManager
from unittest.mock import Mock

from spec.types import App, Spec, Module
from spec.loader import load_spec


check = Mock()
test_middleware_settings = {'max_connections': 100, 'pool_size': 10}


@pytest.fixture
def spec() -> Spec:
    """Mock spec."""
    _spec = load_spec()
    yield _spec


@pytest.fixture
def app(spec) -> App:
    """Mock app."""

    from spec.types import App, JSONResponse

    app = App()
    app.spec = spec

    @app.route('/')
    async def home(request):  # noqa
        return JSONResponse({'status': 'ok'})

    yield app


@pytest.fixture
def client(app):
    """Mock client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_module(app, client):
    """Test module."""

    class TestModule(Module):
        """TestModule."""

        async def middleware(self, scope, receive, send, app=None):  # noqa
            """Test http middleware."""
            check('middleware', self.alias, scope['type'])
            return await app(scope, receive, send)

        async def prepare(self, scope):  # noqa
            """Test prepare hook."""
            check('lifespan', 'startup')

        async def release(self, scope):  # noqa
            """Test release hook."""
            check('lifespan', 'shutdown')

    test = TestModule()

    assert test.alias == 'testmodule'  # noqa

    test.inject(app)
    assert test.active

    assert app.modules
    assert app.modules['testmodule'] is test

    assert test.module_settings == {'alias': 'testmodule'}

    with client:
        res = client.get('/')
        assert res.status_code == 200

    assert [args[0] for args in check.call_args_list] == [
        ('lifespan', 'startup'),
        ('middleware', 'testmodule', 'http'),
        ('lifespan', 'shutdown'),
    ]


def test_module_with_custom_alias(app, client):
    """Test module with overload alias."""

    class TestModule(Module):
        """TestModule."""

        pass

    test = TestModule(
        alias='custom',
        middleware_settings=test_middleware_settings,
    )

    assert test.alias == 'custom'  # noqa

    test.inject(app)
    assert test.active

    assert app.modules
    assert app.modules['custom'] is test

    assert test.module_settings == {'alias': 'custom'}


def test_module_with_settings(app, client):
    """Test module with settings."""

    class TestModule(Module):
        """TestModule."""

        pass

    test = TestModule(
        middleware_settings=test_middleware_settings,
        any_huynya=True,
    )

    test.inject(app)
    assert test.active

    assert app.modules
    assert app.modules['testmodule'] is test

    assert test.middleware_settings == test_middleware_settings
    assert test.module_settings == {'alias': 'testmodule', 'any_huynya': True}


def test_module_active_with_asgi_lifespan(app, client):
    """Test module with settings."""

    class TestModule(Module):
        """TestModule."""
        pass

    test = TestModule()
    test.inject(app)

    async def _emulate_lifespan():
        async with LifespanManager(app):
            assert test.active

    asyncio.run(_emulate_lifespan())


def test_module_not_active_with_lifespan_error(app, client, caplog):
    """Test module with settings."""

    class TestModule(Module):
        """TestModule."""

        async def prepare(self, scope):
            """Emulate prepare module error."""
            raise Exception('Oups')

    test = TestModule()
    test.inject(app)

    async def _emulate_lifespan():
        async with LifespanManager(app):
            assert not test.active

    with caplog.at_level(logging.CRITICAL):
        asyncio.run(_emulate_lifespan())
