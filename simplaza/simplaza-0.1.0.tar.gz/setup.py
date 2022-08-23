# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplaza']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'click>=8.1.3,<9.0.0',
 'magneturi>=1.3,<2.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=12.5.1,<13.0.0']

entry_points = \
{'console_scripts': ['simplaza = simplaza.__main__:main']}

setup_kwargs = {
    'name': 'simplaza',
    'version': '0.1.0',
    'description': 'SimPlaza unoffical CLI - Query and download torrent files from SimPlaza directly from your terminal',
    'long_description': None,
    'author': 'Jacob',
    'author_email': 'jayy2004@gmx.co.uk',
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
