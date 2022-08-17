# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kong']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'aiohttp>=3.8.1,<4.0.0', 'click>=8.1.3,<9.0.0']

setup_kwargs = {
    'name': 'aio-kong',
    'version': '2.8.0',
    'description': 'Asynchronous Kong Client',
    'long_description': '# Async Python Client for Kong\n\n[![PyPI version](https://badge.fury.io/py/aio-kong.svg)](https://badge.fury.io/py/aio-kong)\n[![Python versions](https://img.shields.io/pypi/pyversions/aio-kong.svg)](https://pypi.org/project/aio-kong)\n[![Build](https://github.com/quantmind/aio-kong/workflows/build/badge.svg)](https://github.com/quantmind/aio-kong/actions?query=workflow%3Abuild)\n[![codecov](https://codecov.io/gh/quantmind/aio-kong/branch/master/graph/badge.svg)](https://codecov.io/gh/quantmind/aio-kong)\n[![Downloads](https://img.shields.io/pypi/dd/aio-kong.svg)](https://pypi.org/project/aio-kong/)\n\n\nTested with [kong][] v2.8\n\n## Installation & Testing\n\nTo install the package\n\n```\npip install aio-kong\n```\n\nTo run tests, clone and\n\n```\nmake test\n```\n\n:warning: If you don\'t have Kong or postgres running locally, run the services first\n\n```bash\nmake services\n```\n\ntest certificates were generated using the command\n\n```\nopenssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -nodes -subj \'/CN=localhost\'\n```\n\n## Client\n\nThe client can be imported via\n\n```python\nfrom kong.client import Kong\n```\n\nIn a coroutine:\n\n```python\nasync with Kong() as cli:\n    services = await cli.services.get_list()\n    print(json.dumps([s.data for s in services], indent=2))\n```\n\nBy default the url is obtained from the "KONG_ADMIN_URL" environment variable which defaults to http://127.0.0.1:8001.\n\nThe client has handlers for all Kong objects\n\n- [cli.services](./kong/services.py) CRUD operations on services\n- [cli.routes](./kong/routes.py) CRUD operations on routes\n- [cli.plugins](./kong/plugins.py) CRUD operations on plugins\n- [cli.consumers](./kong/consumers.py) CRUD operations on consumers\n- [cli.certificates](./kong/certificates.py) CRUD operations on TLS certificates\n- [cli.snis](./kong/snis.py) CRUD operations on SNIs\n- `cli.acls` To list all ACLs\n\n### Apply a configuration\n\nThe client allow to apply a configuration object to kong:\n\n```python\nawait cli.apply_json(config)\n```\n\n## Command line tool\n\nThe library install the `kongfig` command line tool for uploading kong configuration files.\n\n```\nkongfig --yaml config.yaml\n```\n\n[kong]: https://github.com/Kong/kong\n',
    'author': 'Luca',
    'author_email': 'luca@quantmind.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
