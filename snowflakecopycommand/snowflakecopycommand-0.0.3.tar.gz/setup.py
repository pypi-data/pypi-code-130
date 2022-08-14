# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snowflakecopycommand']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'snowflakecopycommand',
    'version': '0.0.3',
    'description': 'https://github.com/J-T-R/SnowflakeCopyCommand',
    'long_description': None,
    'author': 'Jo',
    'author_email': 'jthickpennyryan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10',
}


setup(**setup_kwargs)
