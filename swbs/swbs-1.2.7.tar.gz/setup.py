# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['swbs']

package_data = \
{'': ['*']}

install_requires = \
['pycryptodomex>=3.15.0,<4.0.0']

setup_kwargs = {
    'name': 'swbs',
    'version': '1.2.7',
    'description': 'General-purpose socket wrapper for sending and receiving byte strings.',
    'long_description': '![project icon](project-icon.svg)\n# Socket Wrapper for Byte Strings\n[![forthebadge](https://forthebadge.com/images/badges/contains-technical-debt.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)\n\n\n"A straight-forward wrapper for sending and receiving byte strings with sockets."\n\n(Probably) thread safe, allowing for juggling of multiple clients with one server socket instance through threading.\n\n## Documentation\nTo see documentation regarding installation and usage, please visit [the manual for this project](https://dreamerslegacy.xyz/projects/swbs/docs/index.html).\n\n## Releases & Dist.\nWith the released wheel file, after downloading:\n```commandline\npip3 install /path/to/wheel/file/here/swbs-1.2.4-py3-none-any.whl\n```\n...Or available on PyPI through:\n```commandline\npip3 install swbs\n```\nPlease see documentation for more information.\n\n## For Versions < 1.2\nVersions below 1.2 are deprecated and no longer supported. The documentation is no longer available, unless produced from a previous VCS commit.\n',
    'author': 'perpetualCreations',
    'author_email': 'tchen0584@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dreamerslegacy.xyz/git/perpetualCreations/swbs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
