# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['service', 'service.command', 'service.log', 'tests']

package_data = \
{'': ['*']}

modules = \
['README', '.gitignore', 'pyproject']
install_requires = \
['PyYAML>=6.0,<7.0',
 'Pygments>=2.12.0,<3.0.0',
 'dep-spec==0.4.1',
 'fire>=0.4.0,<0.5.0',
 'logging-json>=0.2.1,<0.3.0',
 'pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 'dep-service',
    'version': '1.3.0',
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
