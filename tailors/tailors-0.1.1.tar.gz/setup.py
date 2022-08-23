# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tailors', 'tailors.fast', 'tailors.metrics', 'tailors.utils']

package_data = \
{'': ['*']}

install_requires = \
['einops>=0.4.1,<0.5.0',
 'fasttext>=0.9.2,<0.10.0',
 'ftfy>=6.1.1,<7.0.0',
 'hao>=3.7.0',
 'jieba>=0.42.1,<0.43.0',
 'opencc>=1,<2',
 'seqeval>=1.2.2,<2.0.0',
 'sklearn>=0.0,<0.1',
 'torch>=1.8.1',
 'transformers>=4.11,<5.0']

setup_kwargs = {
    'name': 'tailors',
    'version': '0.1.1',
    'description': '',
    'long_description': '# tailors\n\nabstract base models\n',
    'author': 'orctom',
    'author_email': 'orctom@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/orctom/tailors',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
