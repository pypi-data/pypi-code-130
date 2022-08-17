# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foxplainer']

package_data = \
{'': ['*'], 'foxplainer': ['dataset/*', 'global_model/*']}

install_requires = \
['anytree>=2.8.0,<3.0.0',
 'ipywidgets>=7.7.1,<8.0.0',
 'numpy>=1.23.2,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'python-sat==0.1.7.dev15',
 'scikit-learn>=1.1.2,<2.0.0',
 'six>=1.16.0,<2.0.0']

setup_kwargs = {
    'name': 'foxplainer',
    'version': '0.1.1',
    'description': 'FoX: a Fo rmal eX plainer for JIT Defect Prediction',
    'long_description': None,
    'author': 'Jinqiang Yu',
    'author_email': 'trustablefox@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
