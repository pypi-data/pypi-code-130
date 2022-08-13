from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from pytest import fixture
from unittest.mock import Mock

from plugin import Plugin


check = Mock()


async def health(request):  # noqa
    """Health endpoint."""
    return JSONResponse({'status': 'ok'})


@fixture
def service():
    """Mock service."""
    app = Starlette()
    app.add_route('/', health)
    return app


@fixture
def client(service):
    """Mock client."""
    return TestClient(service)


class CustomPlugin(Plugin):
    """Custom plugin for tests."""

    alias = 'custom'
    options = {'enabled': True, 'workers': 3}

    async def middleware(self, scope, receive, send, app=None):
        """Test embed middleware."""
        check('middleware', self.alias, scope['type'])
        return await app(scope, receive, send)

    async def startup(self, scope):
        """Test embed startup hook."""
        check('lifespan', 'startup')

    async def shutdown(self, scope):
        """Test embed shutdown hook."""
        check('lifespan', 'shutdown')


@fixture
def plugin(service):
    """Mock plugin."""
    yield CustomPlugin()


def test_client(client):
    """Test client."""
    with client:
        response = client.get('/')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


def test_plugin(service, client, plugin):
    """Test plugin."""

    plugin.setup(service, enabled=True, workers=3)

    # check plugin options
    assert plugin.options.enabled
    assert plugin.options.workers == 3

    # check plugin register
    assert service._plugin_store  # noqa
    assert service._plugin_store.custom is plugin  # noqa

    # check health after embed
    with client:
        response = client.get('/')
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}

    # check hooks
    assert [args[0] for args in check.call_args_list] == [
        ('lifespan', 'startup'),
        ('middleware', 'custom', 'http'),
        ('lifespan', 'shutdown'),
    ]
