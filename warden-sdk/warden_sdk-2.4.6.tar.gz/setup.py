# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['warden_sdk', 'warden_sdk.auth', 'warden_sdk.integrations']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0', 'tldextract>=3.3.1,<4.0.0']

setup_kwargs = {
    'name': 'warden-sdk',
    'version': '2.4.6',
    'description': '',
    'long_description': None,
    'author': 'Ferant Tech Corp.',
    'author_email': 'cto@ferant.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
