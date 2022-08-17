# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nelo2_logging_handler']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'requests>=2.23.0,<3.0.0']

setup_kwargs = {
    'name': 'nelo2-logging-handler',
    'version': '0.1.10',
    'description': '',
    'long_description': 'nelo2-logging-handler\n----------------------------\n\nThis is the package for https://www.ncloud.com/product/analytics/elsa\n',
    'author': 'ultimatelife',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ultimatelife/nelo2-logging-handler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.7,<4.0.0',
}


setup(**setup_kwargs)
