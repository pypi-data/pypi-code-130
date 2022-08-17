# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['managed_service_fixtures', 'managed_service_fixtures.services']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'filelock>=3.7.1,<4.0.0',
 'importlib-metadata>=4.12.0,<5.0.0',
 'mirakuru>=2.4.2,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pytest-asyncio>=0.19.0,<0.20.0',
 'pytest-xdist>=2.5.0,<3.0.0',
 'pytest>=7.1.0,<8.0.0']

setup_kwargs = {
    'name': 'managed-service-fixtures',
    'version': '0.1.5',
    'description': 'Pytest fixtures to manage external services such as Cockroach DB, Vault, or Redis',
    'long_description': '# managed-service-fixtures\n\n`managed-service-fixtures` is a collection of [pytest fixtures](https://docs.pytest.org/en/6.2.x/fixture.html) used to manage external processes such as databases, redis, and vault while running integration tests. \n\nTesting Python applications that depend on external services such as a database, redis server, or storing data in Amazon S3 can be difficult. One solution is Unit testing: mock any kind of network IO and isolate tests to your application logic alone. With larger applications, you may find yourself in "mock hell" or discover that you\'re missing real-world bugs.\n\n`managed-service-fixtures` is designed to help you write Integration tests that require an external service be active. In the simplest case, where `pytest` is run serially and manages starting and stopping the service, then `managed-service-fixtures` is basically a wrapper around the excellent [mirakuru.py](https://github.com/ClearcodeHQ/mirakuru) library with some [Pydantic](https://pydantic-docs.helpmanual.io/) modeling for the service connection details. There are two common non-simple use cases this library addresses as well.\n\nThe first non-simple use-case is running tests in parallel with `pytest-xdist`. A naive fixture that starts and stops a service with `mirakuru`, even if it were sessions coped, would end up creating one service for each worker. `managed-service-fixtures` addresses this situation by using `FileLock` and a state file that each worker registers itself in. Only one worker ends up being the manager, responsible for starting the service and then shutting it down once all other workers have unregistered themselves (completed their tests).\n\nThe second non-simple use-case is managing services outside of the `pytest` fixtures. You might want to point your tests towards a service on a remote cluster. You might also want to stop `pytest` from tearing down a database after the tests complete so that you can introspect and debug what is in there. In those cases where you are manually starting and stopping services, you can set environment variables pointing to a file with connection details to those services, then the fixtures in `managed-service-fixtures` will not try to handle lifecycle management itself.\n\n# Example\n\nSee the `tests/` directory for more usage examples.\n\n```python\n# tests/conftest.py\n# https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#using-fixtures-from-other-projects\n\npytest_plugins = \'managed_service_fixtures\'\n```\n\n```python\n# tests/test_vault.py\nimport hvac\nfrom managed_service_fixtures import VaultDetails\n\n\ndef test_vault_connection(managed_vault: VaultDetails):\n    client = hvac.Client(url=managed_vault.url, token=managed_vault.token)\n    assert client.is_authenticated()\n    assert client.sys.is_initialized()\n    assert not client.sys.is_sealed()\n```\n\n# Fixtures\n\nYou may need to install a system library or CLI depending on which service you want to manage with `mirakuru` / `managed-service-fixtures`.\n\n - `managed_cockroach` starts an in-memory instance of [CockroachDB](https://www.cockroachlabs.com/docs/stable/frequently-asked-questions.html), see [install instructions](https://www.cockroachlabs.com/docs/stable/install-cockroachdb.html) for setting up the `cockroach` CLI\n - `managed_moto` starts a [Moto - Mock AWS Service](https://github.com/spulec/moto), `pip install moto` to enable the CLI\n - `managed_redis` starts a [Redis](https://redis.io/) server, See [install instructions](https://redis.io/docs/getting-started/installation/) to enable the `redis-server` CLI\n - `managed_vault` starts a [Vault](https://www.vaultproject.io/) server, see [install instructions](https://www.vaultproject.io/docs/install) to enable the `vault` CLI\n\n# ASGI apps\n\n`managed-service-fixtures` supports running an ASGI app (such as a [FastAPI](https://fastapi.tiangolo.com/) or [Starlette](https://www.starlette.io/) app) with `uvicorn` as a managed service. You may want to use this if:\n \n - You\'re using `httpx.AsyncClient` for [async tests](https://fastapi.tiangolo.com/advanced/async-tests/) and need to test websocket endpoints\n - You have a `websockets` application/library and need to spin up a server to test request/responses\n\nA downside to running an ASGI app in an external process is that you lose breakpoint/debug support in your tests.\n\n\n',
    'author': 'Noteable Engineering',
    'author_email': 'engineering-backend@noteable.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/noteable-io/managed-service-fixtures',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
