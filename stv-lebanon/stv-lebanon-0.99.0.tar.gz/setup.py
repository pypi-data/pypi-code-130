# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stv_lebanon', 'stv_lebanon.samples']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['stvlebanon = stv_lebanon.cli_interface:main']}

setup_kwargs = {
    'name': 'stv-lebanon',
    'version': '0.99.0',
    'description': 'Library for the Single Transferrable Vote version for Lebanon',
    'long_description': None,
    'author': 'Robert Trad',
    'author_email': 'roberttrad@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
