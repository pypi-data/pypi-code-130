# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['JCompile']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['jcompyle = run:run']}

setup_kwargs = {
    'name': 'jcompyle',
    'version': '0.1.2',
    'description': 'simple json compiler',
    'long_description': None,
    'author': 'amir',
    'author_email': 'amir.daaee@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
