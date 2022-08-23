# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stockcli']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0',
 'mplfinance>=0.12.9-beta.1,<0.13.0',
 'prettytable>=3.3.0,<4.0.0',
 'typer[all]>=0.6.1,<0.7.0',
 'yfinance>=0.1.74,<0.2.0']

entry_points = \
{'console_scripts': ['stockcli = stockcli.main:app']}

setup_kwargs = {
    'name': 'stockcli',
    'version': '0.2.0',
    'description': 'This is a CLI tool to retrieve data from yahoo finance',
    'long_description': '# stockcli\n\n## _This is a CLI tool to retrieve data from [finance.yahoo.com](https://finance.yahoo.com/)._\n\n#### Available commands\n\n![cli](https://i.ibb.co/j43zt5L/cli.png)',
    'author': 'hasindu sithmin',
    'author_email': 'hasindusithmin64@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hasindusithmin/financecli.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
