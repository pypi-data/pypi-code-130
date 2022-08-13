# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plugin', 'tests']

package_data = \
{'': ['*']}

modules = \
['README', '.gitignore', 'pyproject']
setup_kwargs = {
    'name': 'dep-plugin',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'everhide',
    'author_email': 'i.tolkachnikov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
