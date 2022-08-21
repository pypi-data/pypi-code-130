# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_cqase']

package_data = \
{'': ['*']}

install_requires = \
['cqase-client>=0.1.1,<0.2.0', 'filelock>=3.8.0,<4.0.0', 'pytest>=7.1.2,<8.0.0']

entry_points = \
{'pytest11': ['name_of_plugin = pytest_cqase.conftest']}

setup_kwargs = {
    'name': 'pytest-cqase',
    'version': '0.1.11',
    'description': 'Custom qase pytest plugin',
    'long_description': None,
    'author': 'alexanderlozovoy',
    'author_email': 'berpress@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/berpress/cqase-pytest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
