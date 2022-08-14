# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hdtorch']

package_data = \
{'': ['*'], 'hdtorch': ['cuda/*']}

setup_kwargs = {
    'name': 'hdtorch',
    'version': '1.0.0',
    'description': 'HDTorch: Accelerating Hyperdimensional Computing with GP-GPUs for Design Space Exploration',
    'long_description': 'This is a readme',
    'author': 'wasimon',
    'author_email': 'william.simon@epfl.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://c4science.ch/source/hdtorch/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
