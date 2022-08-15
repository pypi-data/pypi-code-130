# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['selenium_setup']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0',
 'rich>=12.5.1,<13.0.0',
 'selenium',
 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'selenium-setup',
    'version': '0.0.0',
    'description': '',
    'long_description': '# selenium_setup\n\n[![pypi](https://img.shields.io/pypi/v/selenium_setup?color=%2334D058)](https://pypi.org/project/selenium_setup/)\n\n## install\n\n```shell\npip install selenium_setup\n```\n\n## setup\n\n```shell\npython -m selenium_setup\n```\n',
    'author': ' ',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/m9810223/selenium_setup',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
