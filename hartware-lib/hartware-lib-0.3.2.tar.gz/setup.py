# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hartware_lib',
 'hartware_lib.adapters',
 'hartware_lib.commands',
 'hartware_lib.exceptions',
 'hartware_lib.pydantic',
 'hartware_lib.settings',
 'hartware_lib.utils']

package_data = \
{'': ['*']}

install_requires = \
['requests-mock>=1.9.3,<2.0.0', 'types-requests>=2.27.16,<3.0.0']

extras_require = \
{'all': ['slack-sdk>=3.11.2,<4.0.0',
         'pydantic>=1.9.0,<2.0.0',
         'aiofiles>=0.8.0,<0.9.0'],
 'async': ['aiofiles>=0.8.0,<0.9.0'],
 'pydantic': ['pydantic>=1.9.0,<2.0.0'],
 'slack': ['slack-sdk>=3.11.2,<4.0.0']}

entry_points = \
{'console_scripts': ['slack_send = hartware_lib.commands.slack:slack_send']}

setup_kwargs = {
    'name': 'hartware-lib',
    'version': '0.3.2',
    'description': 'Core helper lib for Hartware codes.',
    'long_description': '# Hartware Lib\n',
    'author': 'Laurent Arthur',
    'author_email': 'laurent.arthur75@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/ludwig778/python-lib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
