# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['learna', 'learna.activations']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.3,<4.0.0', 'numpy>=1.23.2,<2.0.0', 'scipy>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'learna',
    'version': '0.1.1',
    'description': 'Machine learning implemented purely in python. Mainly for research and learning purposes.',
    'long_description': '# learna\n\nMachine learning library\n',
    'author': 'Naveen Anil',
    'author_email': 'naveenms01@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nvn-nil/learna',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
