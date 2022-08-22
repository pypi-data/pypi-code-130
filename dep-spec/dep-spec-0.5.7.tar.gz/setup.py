# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spec', 'spec.ext', 'spec.service', 'tests']

package_data = \
{'': ['*']}

modules = \
['README', '.gitignore', 'pyproject']
install_requires = \
['Faker>=14.0.0,<15.0.0',
 'fastapi>=0.79.0,<0.80.0',
 'flake8-bandit>=3.0.0,<4.0.0',
 'flake8-docstrings>=1.6.0,<2.0.0',
 'flake8==3.9.0',
 'flakehell>=0.9.0,<0.10.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'uvicorn>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'dep-spec',
    'version': '0.5.7',
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
