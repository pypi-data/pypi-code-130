"""Check plugins."""

from fastapi.testclient import TestClient
from pytest import fixture
from unittest.mock import Mock

from spec import load_spec
from spec.types import App, Route, Spec, Plugin, Middleware


check = Mock()


@fixture
async def mock_app() -> App:
    """Mock app."""
    async def index():  # noqa
        return {'status': 'ok'}
    yield App(routes=[Route('/', index)])


@fixture
def spec() -> Spec:
    """Mock spec."""
    spec = load_spec()
    yield spec


@fixture
def env_plugin_options(monkeypatch):
    """Plugin options."""

    monkeypatch.setenv('PLUGIN_MONGO_DEFAULT_URI', 'any')
    monkeypatch.setenv('PLUGIN_MONGO_DEFAULT_POOL_SIZE', '1')

    yield

    monkeypatch.delenv('PLUGIN_MONGO_DEFAULT_URI', raising=False)
    monkeypatch.delenv('PLUGIN_MONGO_DEFAULT_POOL_SIZE', raising=False)


@fixture
def mock_client(mock_app):
    """Mock app client."""
    with TestClient(mock_app) as client:  # noqa
        return client


class CustomMiddleware(Middleware):
    """Custom plugin middleware."""

    def __init__(self, app, **kwargs) -> None:
        """Init."""
        super().__init__(app, **kwargs)
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        """Call."""
        check('lifespan', 'http')
        await self.app(scope, receive, send)


class Mongo(Plugin):
    """Custom plugin."""

    type_name = 'mongo'

    middleware = CustomMiddleware

    async def prepare(self, app: App, spec: Spec) -> None:  # noqa
        """Check prepare hook."""
        check('lifespan', 'startup')

    async def release(self, app: App, spec: Spec) -> None:  # noqa
        """Check shutdown hook."""
        check('lifespan', 'shutdown')


async def test_plugin_create(env_plugin_options, mock_app, spec, mock_client):
    """Test plugin create."""

    plugin = Mongo(alias='default')

    plugin.inject(mock_app, spec=spec)

    assert plugin.alias == 'default'
    assert plugin.fqdn == 'mongo.default'
    assert plugin.env

    await plugin.prepare(mock_app, spec=spec)
    await plugin.release(mock_app, spec=spec)

    assert 'pool_size' in plugin.env
    assert 'uri' in plugin.env

    assert plugin.env['uri'] == 'any'
    assert plugin.env['pool_size'] == '1'

    response = mock_client.get('/')
    assert response.status_code == 200

    assert mock_app.plugins(plugin.fqdn) == plugin

    assert [args[0] for args in check.call_args_list] == [
        ('lifespan', 'startup'),
        ('lifespan', 'shutdown'),
        ('lifespan', 'http'),
    ]
