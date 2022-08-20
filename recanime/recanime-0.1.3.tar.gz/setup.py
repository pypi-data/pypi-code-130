# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['recanime',
 'recanime.anime_store',
 'recanime.recommender',
 'recanime.recommender.ranking_base_filter',
 'recanime.schema',
 'recanime.training',
 'recanime.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'torch>=1.12.0,<2.0.0']

setup_kwargs = {
    'name': 'recanime',
    'version': '0.1.3',
    'description': 'Anime recommender system builded by Pytorch',
    'long_description': None,
    'author': 'yoshi',
    'author_email': 'yoshi4868686@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
