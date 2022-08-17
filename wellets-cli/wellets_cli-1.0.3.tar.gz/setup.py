# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wellets_cli', 'wellets_cli.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'inquirerpy>=0.3.4,<0.4.0',
 'pydantic>=1.9.1,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'requests>=2.28.1,<3.0.0',
 'tabulate>=0.8.10,<0.9.0']

entry_points = \
{'console_scripts': ['wellets_cli = wellets_cli.__main__:main']}

setup_kwargs = {
    'name': 'wellets-cli',
    'version': '1.0.3',
    'description': 'wellets-cli is the command line interface for Wellets, a crypto-oriented financial management tool that allows you to keep under control your money.',
    'long_description': None,
    'author': 'lparolari',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
