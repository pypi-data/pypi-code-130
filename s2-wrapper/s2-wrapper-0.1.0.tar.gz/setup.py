# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['s2_wrapper',
 's2_wrapper.api',
 's2_wrapper.api.academic_graph',
 's2_wrapper.api.academic_graph.v1',
 's2_wrapper.api.datasets',
 's2_wrapper.api.peer_review',
 's2_wrapper.api.recommendations']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 's2-wrapper',
    'version': '0.1.0',
    'description': 'A wrapper for the Semantic Scholar API',
    'long_description': None,
    'author': 'Gabriel Martín Blázquez',
    'author_email': 'gmartinbdev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
