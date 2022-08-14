# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ingresso']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'ingresso',
    'version': '0.1.0',
    'description': 'A wrapper python para o ingresso.com',
    'long_description': None,
    'author': 'Hudson Brendon',
    'author_email': 'contato.hudsonbrendon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
