# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spacy_lefff']

package_data = \
{'': ['*'], 'spacy_lefff': ['data/*']}

install_requires = \
['black>=22.6.0,<23.0.0',
 'msgpack>=0.3.0,<0.6',
 'pluggy>=0.12.0',
 'spacy',
 'tqdm>=4.11.1']

setup_kwargs = {
    'name': 'spacy-lefff',
    'version': '0.5.1',
    'description': 'Custom French POS and lemmatizer based on Lefff for spacy',
    'long_description': None,
    'author': 'Sami Moustachir',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sammous/spacy-lefff',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
