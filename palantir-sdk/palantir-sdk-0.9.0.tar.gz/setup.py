# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['palantir', 'palantir.core', 'palantir.datasets', 'palantir.datasets.rpc']

package_data = \
{'': ['*']}

install_requires = \
['conjure-python-client>=2.1.0,<3.0.0', 'tomli>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'palantir-sdk',
    'version': '0.9.0',
    'description': 'Palantir Python SDK',
    'long_description': None,
    'author': 'Andrew Higgins',
    'author_email': 'ahiggins@palantir.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/palantir/palantir-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
