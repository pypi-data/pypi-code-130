# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nlp_dataset']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nlp-dataset',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'waylight3',
    'author_email': 'waylight3@snu.ac.kr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
