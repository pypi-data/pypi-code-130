# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['switchbot_cloud']

package_data = \
{'': ['*']}

install_requires = \
['pyhumps>=3.0.2,<4.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'switchbot-cloud',
    'version': '0.2.5',
    'description': 'A Python API client for controlling SwitchBot devices via the SwitchBot Cloud API',
    'long_description': None,
    'author': 'Eric Abruzzese',
    'author_email': 'eric.abruzzese@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
