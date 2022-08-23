# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nsj_flask_auth', 'nsj_flask_auth.exceptions']

package_data = \
{'': ['*']}

install_requires = \
['Flask', 'requests']

setup_kwargs = {
    'name': 'nsj-flask-auth',
    'version': '0.1.7',
    'description': 'Modulo básico para autenticação de aplicações Flask no contexto da Nasajon',
    'long_description': None,
    'author': 'Lucas Assis',
    'author_email': 'lucasassis@nasajon.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
