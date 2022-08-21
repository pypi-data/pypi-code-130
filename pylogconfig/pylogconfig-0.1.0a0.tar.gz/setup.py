# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pylogconfig']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pylogconfig',
    'version': '0.1.0a0',
    'description': 'Easily configure Python logger with configuration files.',
    'long_description': None,
    'author': 'RemyLau',
    'author_email': 'remylau961@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
