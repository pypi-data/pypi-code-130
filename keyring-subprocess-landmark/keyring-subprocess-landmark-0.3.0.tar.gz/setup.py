# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['keyring_subprocess_landmark']

package_data = \
{'': ['*']}

install_requires = \
['keyring', 'keyring-subprocess']

entry_points = \
{'console_scripts': ['keyring-subprocess = '
                     'keyring_subprocess_landmark:keyring_subprocess']}

setup_kwargs = {
    'name': 'keyring-subprocess-landmark',
    'version': '0.3.0',
    'description': '',
    'long_description': 'Intended to be installed indirectly by installing `keyring-subprocess[landmark]`',
    'author': 'Dos Moonen',
    'author_email': 'darsstar@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/Darsstar/keyring-subprocess-landmark',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
