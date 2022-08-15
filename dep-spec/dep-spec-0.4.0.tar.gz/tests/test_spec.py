"""Spec testing."""

import os

from pathlib import Path
from tempfile import gettempdir

from spec import fn, Spec
from spec import types, load_spec
from spec.default import get


def test_defaults(default_spec):
    """Test defaults values."""
    for (alias, cast_type, right_value) in default_spec:
        eval_value = fn.env(alias, cast=cast_type)
        assert eval_value == right_value


def test_as_dict(pyproject):
    """Test as dict."""
    spec = load_spec()
    as_dict = spec.as_dict()
    as_dict_keys = (
        'socket',
        'info',
        'runtime',
        'paths',
        'policy',
        'i18n',
        'sentry_dsn',
        'log_level',
    )

    for dict_key in as_dict_keys:
        assert dict_key in as_dict.keys()


def test_spec_with_defaults(pyproject):
    """Test spec with default values."""

    spec = load_spec()

    assert isinstance(spec, Spec)

    assert spec.doc.enabled
    assert spec.doc.prefix == '/doc'
    assert not spec.doc.blm

    assert spec.log_level == get('LOG_LEVEL')
    assert spec.sentry_dsn == get('SENTRY_DSN')

    assert spec.socket == types.Socket(
        host=get('SERVICE_HOST'),
        port=get('SERVICE_PORT'),
        scheme=get('SERVICE_SCHEME_INSECURE'),
    )

    assert spec.info == types.Info(
        verbose_name=get('SERVICE_NAME'),
        tech_name=pyproject['tool']['poetry']['name'],
        version=pyproject['tool']['poetry']['version'],
        description=pyproject['tool']['poetry']['description'],
    )

    assert spec.policy == types.Policy(
        service_workers=get('POLICY_SERVICE_WORKERS'),
        db_pool_size=get('POLICY_DB_POOL_SIZE'),
        db_max_connections=get('POLICY_DB_MAX_CONNECTIONS'),
        request_timeout=get('POLICY_REQUEST_TIMEOUT'),
        request_retry_max=get('POLICY_REQUEST_RETRY_MAX'),
        scheduler_enabled=get('POLICY_SCHEDULER_ENABLED'),
        scheduler_persistent=get('POLICY_SCHEDULER_PERSISTENT'),
        scheduler_workers=get('POLICY_SCHEDULER_WORKERS'),
        scheduler_instances=get('POLICY_SCHEDULER_INSTANCES'),
        scheduler_coalesce=get('POLICY_SCHEDULER_COALESCE'),
        scheduler_host=get('POLICY_SCHEDULER_HOST'),
        scheduler_port=get('POLICY_SCHEDULER_PORT'),
        scheduler_db=get('POLICY_SCHEDULER_DB'),
    )

    assert spec.paths == types.Paths(
        app=Path(os.getcwd()).resolve(),
        temp=Path(gettempdir()).resolve(),
        assets=Path(spec.paths.app / 'assets').resolve(),
        i18n=Path(spec.paths.assets / 'i18n').resolve(),
        media=Path(spec.paths.assets / 'media').resolve(),
        static=Path(spec.paths.assets / 'static').resolve(),
        pyproject=Path(spec.paths.app / 'pyproject.toml').resolve(),
        log_config_name=None,
        log_config_path=None,
    )

    all_codes = [get('I18N_LANG')]
    all_codes += get('I18N_SUPPORT')

    assert spec.i18n == types.I18N(
        lang=get('I18N_LANG'),
        support_codes=get('I18N_SUPPORT'),
        locales=get('I18N_LOCALES'),
        all_codes=all_codes,
    )

    assert spec.runtime == types.Runtime(
        debug=get('DEBUG'),
        environment=get('ENVIRONMENT'),
        entrypoint=fn.env('SERVICE_ENTRYPOINT', cast=str),
        testing=fn.is_testing(),
        on_k8s=fn.on_k8s(),
    )


def test_k8s_on(pyproject, k8s_running):  # noqa
    """Test spec with default values."""

    assert fn.on_k8s()

    spec = load_spec()
    assert spec.runtime.on_k8s
