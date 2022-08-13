# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['server']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'openapi-core>=0.14.2,<0.15.0',
 'starlette>=0.19.0,<0.20.0',
 'stringcase>=1.2.0,<2.0.0']

extras_require = \
{'uvicorn': ['uvicorn>=0.18.2,<0.19.0']}

setup_kwargs = {
    'name': 'pyapi-server',
    'version': '0.1.0',
    'description': 'Lightweight API framework using an OpenAPI spec for routing and validation.',
    'long_description': '# PyAPI Server\n\n**PyAPI Server** is a Python library for serving REST APIs based on\n[OpenAPI](https://swagger.io/resources/open-api/) specifications. It is based on [Starlette](https://www.starlette.io) and is functionally very similar to [connexion](https://connexion.readthedocs.io), except that it aims to be fully [ASGI](https://asgi.readthedocs.io)-compliant.\n\n**WARNING:** This is still a work in progress and not quite ready for production usage. Until version 1.0 is released, any new release can be expected to break backward compatibility.\n\n\n## Quick Start\n\n```python\nfrom pyapi.server import Application\nfrom some.path import endpoints\n\napp = Application.from_file("path/to/openapi.yaml", module=endpoints)\n```\n',
    'author': 'Berislav Lopac',
    'author_email': 'berislav@lopac.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pyapi-server.readthedocs.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
