# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyexplainer']

package_data = \
{'': ['*'],
 'pyexplainer': ['css/*',
                 'default_data/*',
                 'dev_info/*',
                 'js/*',
                 'rf_models/*']}

install_requires = \
['ipython>=7.16.0,<8.0.0',
 'ipywidgets>=7.6.3,<8.0.0',
 'numpy>=1.19.0,<2.0.0',
 'pandas>=1.1.0,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.5.0,<2.0.0',
 'statsmodels>=0.12.2,<0.13.0']

setup_kwargs = {
    'name': 'pyexplainer',
    'version': '1.2.0',
    'description': 'Explainable AI tool for Software Quality Assurance (SQA)',
    'long_description': None,
    'author': 'Michael',
    'author_email': 'michaelfu1998@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
