"""Test modules."""

from pytest import fixture
from unittest.mock import Mock

from spec.types import Module

check = Mock()
test_middleware_settings = {'max_connections': 100, 'pool_size': 10}


@fixture
def app():
    """Mock app."""

    from spec.types import App, JSONResponse

    app = App()

    @app.route('/')
    async def home(request):  # noqa
        return JSONResponse({'status': 'ok'})

    return app


@fixture
def client(app):
    """Mock client."""
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_module(app, client):
    """Test module."""

    class TestModule(Module):
        """TestModule."""

        alias = 'test'

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

    test = TestModule(alias='test')
    assert test

    test.inject(app)

    assert app.modules
    assert app.modules['test'] is test

    assert test.module_settings == {'alias': 'test'}

    with client:
        res = client.get('/')
        assert res.status_code == 200

    assert [args[0] for args in check.call_args_list] == [
        ('lifespan', 'startup'),
        ('middleware', 'test', 'http'),
        ('lifespan', 'shutdown'),
    ]


def test_module_with_settings(app, client):
    """Test module with settings."""

    class TestModule(Module):
        """TestModule."""

        alias = 'test'

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

    test = TestModule(
        alias='test',
        middleware_settings=test_middleware_settings,
        any_huynya=True,
    )

    assert test

    test.inject(app)

    assert app.modules
    assert app.modules['test'] is test

    assert test.middleware_settings == test_middleware_settings
    assert test.module_settings == {'alias': 'test', 'any_huynya': True}
