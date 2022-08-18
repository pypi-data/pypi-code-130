# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pft']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.2,<2.0.0', 'pytest>=7.1.2,<8.0.0', 'torch>=1.12.1,<2.0.0']

setup_kwargs = {
    'name': 'pft',
    'version': '0.1.1',
    'description': 'Extract principal FFT components for features generation implemented in pytorch',
    'long_description': '# Principal FFT Torch\n\nAn implementation of https://github.com/eloquentarduino/principal-fft for pytorch.\n',
    'author': 'Alex',
    'author_email': 'adrysdale@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/abdrysdale/principal-fft-torch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
