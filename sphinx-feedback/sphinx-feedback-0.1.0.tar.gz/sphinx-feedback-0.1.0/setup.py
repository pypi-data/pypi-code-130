# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sphinx_feedback']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sphinx-feedback',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Balaji Veeramani',
    'author_email': 'bveeramani@berkeley.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
