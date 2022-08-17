# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fsdev']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0']

entry_points = \
{'console_scripts': ['fsdev = fsdev.cli:run']}

setup_kwargs = {
    'name': 'fsdev',
    'version': '0.1.0',
    'description': 'A super simple filesystem dev server',
    'long_description': None,
    'author': 'Tristan Slater',
    'author_email': 'hello@trslater.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
