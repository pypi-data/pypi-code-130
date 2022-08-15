# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pybasic']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.2,<2.0.0',
 'opencv-python>=4.6.0,<5.0.0',
 'scipy>=1.9.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['basic_shading_correction = '
                     'scripts.basic_shading_correction:main']}

setup_kwargs = {
    'name': 'pybasic-illumination-correction',
    'version': '0.1.1',
    'description': 'Python Implementation of the BaSiC shading correction algorithm',
    'long_description': None,
    'author': 'Joël Lefebvre',
    'author_email': 'lefebvre.joel@uqam.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/linum-uqam/PyBaSiC',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
