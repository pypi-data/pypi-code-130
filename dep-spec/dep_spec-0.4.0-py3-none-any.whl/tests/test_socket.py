"""Test socket."""

from spec import load_spec


def test_socket_overload_insecure(
    pyproject,  # noqa
    monkeypatch,
):
    """Test sentry on k8s and not testing environment."""

    monkeypatch.setenv('SERVICE_HOST', '127.0.0.1')
    monkeypatch.setenv('SERVICE_PORT', '7070')

    spec = load_spec()

    assert spec.socket.host == '127.0.0.1'
    assert spec.socket.port == 7070
    assert spec.socket.scheme == 'http'


def test_socket_overload_secure(
    pyproject,  # noqa
    k8s_running,
    monkeypatch,
):
    """Test sentry on k8s and not testing environment."""

    monkeypatch.setenv('SERVICE_HOST', '127.0.0.2')
    monkeypatch.setenv('SERVICE_PORT', '9090')

    spec = load_spec()

    assert spec.socket.host == '127.0.0.2'
    assert spec.socket.port == 9090
    assert spec.socket.scheme == 'https'
