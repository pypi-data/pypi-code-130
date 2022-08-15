# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['llunar',
 'llunar.compiler',
 'llunar.lexical',
 'llunar.parser',
 'llunar.parser.binary',
 'llunar.parser.expressions',
 'llunar.parser.functions',
 'llunar.parser.statements']

package_data = \
{'': ['*']}

install_requires = \
['astpretty>=3.0.0,<4.0.0',
 'black>=22.6.0,<23.0.0',
 'isort>=5.10.1,<6.0.0',
 'rply>=0.7.8,<0.8.0']

setup_kwargs = {
    'name': 'llunar',
    'version': '0.1.0',
    'description': 'A PVM language',
    'long_description': None,
    'author': 'andy',
    'author_email': 'andy.development@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/an-dyy/Lunar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
