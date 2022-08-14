# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bashdict']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bashdict',
    'version': '0.1.1',
    'description': 'A simple commandline dictionary',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '==3.10.5',
}


setup(**setup_kwargs)
