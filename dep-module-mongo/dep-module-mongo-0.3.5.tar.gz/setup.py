# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dep_mongo', 'tests']

package_data = \
{'': ['*']}

modules = \
['pyproject']
install_requires = \
['beanie>=1.11.9,<2.0.0', 'dep-spec==0.5.5']

setup_kwargs = {
    'name': 'dep-module-mongo',
    'version': '0.3.5',
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
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
