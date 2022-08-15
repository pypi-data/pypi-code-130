"""Testing sentry."""

from spec import load_spec


def test_sentry_default(pyproject, env_sentry_dsn, monkeypatch):  # noqa
    """Test not sentry with unknown env not on k8s."""
    spec = load_spec()
    assert not spec.runtime.on_k8s
    assert not spec.sentry_dsn


def test_sentry_local_disabled(pyproject, env_sentry_dsn, monkeypatch):  # noqa
    """Test sentry not on k8s and not testing environment."""
    monkeypatch.setenv('ENVIRONMENT', 'develop')
    spec = load_spec()
    assert not spec.runtime.on_k8s
    assert not spec.sentry_dsn


def test_sentry_k8s_enabled(
    pyproject,  # noqa
    k8s_running,  # noqa
    env_sentry_dsn,  # noqa
    monkeypatch,
):
    """Test sentry on k8s and not testing environment."""
    monkeypatch.setenv('ENVIRONMENT', 'develop')
    spec = load_spec()
    assert spec.runtime.on_k8s
    assert spec.sentry_dsn
