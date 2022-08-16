# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jwt_smithy']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT[crypto]>=2.4.0,<3.0.0', 'typer[all]>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'jwt-smithy',
    'version': '1.0.0',
    'description': 'Simple cli tool for jwt keys generation',
    'long_description': '# JWT smithy 🔨\n\n---\n\nSimple cli tool for jwt keys generation\n',
    'author': 'ilyakochankov',
    'author_email': 'ilyakochankov@yandex.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/KochankovID/jwt_smithy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
