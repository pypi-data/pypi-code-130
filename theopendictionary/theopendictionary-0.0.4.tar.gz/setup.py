# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['odict']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'theopendictionary',
    'version': '0.0.4',
    'description': '',
    'long_description': None,
    'author': 'Tyler Nickerson',
    'author_email': 'nickersoft@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
