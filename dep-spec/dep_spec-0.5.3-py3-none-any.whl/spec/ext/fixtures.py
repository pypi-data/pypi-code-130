"""Fixtures."""

from pytest import fixture

from spec.types import App, Spec
from spec.loader import load_spec


@fixture
def spec() -> Spec:
    """Mock spec."""
    _spec = load_spec()
    yield _spec


@fixture
def app(spec) -> App:
    """Mock app."""

    from spec.types import App, JSONResponse

    app = App()
    app.spec = spec

    @app.route('/')
    async def home(request):  # noqa
        return JSONResponse({'status': 'ok'})

    yield app


@fixture
def client(app):
    """Mock client."""
    from fastapi.testclient import TestClient
    return TestClient(app)
