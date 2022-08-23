# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['timewise']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=5.1,<6.0',
 'backoff>=2.1.2,<3.0.0',
 'coveralls>=3.3.1,<4.0.0',
 'furo>=2022.6.21,<2023.0.0',
 'matplotlib>=3.5.3,<4.0.0',
 'myst-parser>=0.18.0,<0.19.0',
 'numpy>=1.23.2,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pyvo>=1.3,<2.0',
 'requests>=2.28.1,<3.0.0',
 'scikit-image>=0.19.3,<0.20.0',
 'tqdm>=4.64.0,<5.0.0',
 'virtualenv>=20.16.3,<21.0.0']

setup_kwargs = {
    'name': 'timewise',
    'version': '0.1.10',
    'description': 'A small package to download infrared data from the WISE satellite',
    'long_description': None,
    'author': 'Jannis Necker',
    'author_email': 'jannis.necker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
