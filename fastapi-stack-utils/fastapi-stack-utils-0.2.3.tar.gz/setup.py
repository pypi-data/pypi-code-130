# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_stack_utils']

package_data = \
{'': ['*']}

install_requires = \
['asgi-correlation-id>=3.0.0,<4.0.0', 'fastapi>0.68.0']

setup_kwargs = {
    'name': 'fastapi-stack-utils',
    'version': '0.2.3',
    'description': 'Utils to extend the FastAPI with logging and exception handlers',
    'long_description': None,
    'author': 'Jonas Krüger Svensson',
    'author_email': 'jonas-ks@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
