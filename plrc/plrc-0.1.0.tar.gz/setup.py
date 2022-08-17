# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plrc',
 'plrc.compiler',
 'plrc.parser',
 'plrc.transformer',
 'plrc.transformer.binary',
 'plrc.transformer.expr',
 'plrc.transformer.functions',
 'plrc.transformer.stmts',
 'plrc.visitor']

package_data = \
{'': ['*']}

install_requires = \
['astpretty>=3.0.0,<4.0.0',
 'black>=22.6.0,<23.0.0',
 'isort>=5.10.1,<6.0.0',
 'lark>=1.1.2,<2.0.0']

setup_kwargs = {
    'name': 'plrc',
    'version': '0.1.0',
    'description': 'Polaris language compiler.',
    'long_description': None,
    'author': 'andy',
    'author_email': 'andy.development@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/an-dyy/Polaris',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
