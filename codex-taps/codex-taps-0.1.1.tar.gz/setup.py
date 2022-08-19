# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codex_taps']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=37.0.4,<38.0.0',
 'requests>=2.28.1,<3.0.0',
 'rich>=12.5.1,<13.0.0',
 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'codex-taps',
    'version': '0.1.1',
    'description': 'This is the checker for final round of CODEx.',
    'long_description': None,
    'author': 'Arpan Pandey',
    'author_email': 'arpan@hackersreboot.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
