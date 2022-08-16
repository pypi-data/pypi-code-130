"""Test uvicorn kw."""

import pytest

from spec import load_spec
from service.command.run import uvicorn_options


@pytest.fixture
def pyproject(mocker):
    """Mock pyproject."""
    fake_pyproject = {
        'tool': {
            'poetry': {
                'name': 'service-name',
                'version': '1.2.3',
                'description': 'Service description',
            },
        },
    }

    mocker.patch('spec.fn.load_pyproject', return_value=fake_pyproject)
    return fake_pyproject


def test_uvicorn_options():
    """Test uvicorn options."""

    spec = load_spec()
    options = uvicorn_options(spec)

    assert options['app'] == spec.runtime.entrypoint
    assert options['host'] == spec.socket.host
    assert options['port'] == spec.socket.port
    assert options['use_colors'] != spec.runtime.on_k8s
    assert options['log_level'] == spec.log_level
    assert 'log_config' not in options
    assert options['access_log'] == spec.runtime.debug
    assert options['workers'] == spec.policy.service_workers
