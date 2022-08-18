# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['morningstreams', 'morningstreams.core']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['ms-install = morningstreams.main:install',
                     'ms-run = morningstreams.main:run']}

setup_kwargs = {
    'name': 'morningstreams',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'S1M0N38',
    'author_email': 'bertolottosimone@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
