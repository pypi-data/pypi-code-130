# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_sentence_segment',
 'fast_sentence_segment.bp',
 'fast_sentence_segment.dmo',
 'fast_sentence_segment.svc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'fast-sentence-segment',
    'version': '0.1.0',
    'description': 'Fast and Efficient Sentence Segmentation',
    'long_description': None,
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
