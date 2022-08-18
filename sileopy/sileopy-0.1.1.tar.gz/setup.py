# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sileopy']

package_data = \
{'': ['*']}

install_requires = \
['opsgenie-sdk>=2.1.5,<3.0.0',
 'paramiko>=2.11.0,<3.0.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'sileopy',
    'version': '0.1.1',
    'description': 'Ett bibliotek för python-moduler med allmän funktionalitet som kan vara användbar i flera projekt.',
    'long_description': None,
    'author': 'Johan Magnusson',
    'author_email': 'johan.magnusson@sileokapital.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
