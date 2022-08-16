# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dep-mongo', 'tests']

package_data = \
{'': ['*']}

modules = \
['pyproject']
install_requires = \
['dep-spec==0.4.1', 'motor>=3.0.0,<4.0.0']

setup_kwargs = {
    'name': 'dep-module-mongo',
    'version': '0.2.0',
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
