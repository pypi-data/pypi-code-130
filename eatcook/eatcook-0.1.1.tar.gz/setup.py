# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['eatcook']
install_requires = \
['colorama>=0.4.5,<0.5.0', 'shellingham>=1.5.0,<2.0.0', 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'eatcook',
    'version': '0.1.1',
    'description': 'Eatcook is a http server that uses socket.',
    'long_description': None,
    'author': 'Zayne Marsh',
    'author_email': 'saynemarsh9@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/porplax/eatcook.',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
