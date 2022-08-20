# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantic_memory']

package_data = \
{'': ['*']}

install_requires = \
['inflect>=6.0.0,<7.0.0',
 'nltk>=3.7,<4.0',
 'numpy>=1.23.2,<2.0.0',
 'torch>=1.12.1,<2.0.0']

setup_kwargs = {
    'name': 'semantic-memory',
    'version': '0.1.0',
    'description': 'A utility package to create semantic memories consisting of concepts, properties, categorical organization, and vector spaces.',
    'long_description': '# semantic-memory\nA utility package to create semantic memories consisting of concepts, properties, categorical organization, and vector spaces.\n\n# Usage\n```py\n# TODO: add code.\n```\n',
    'author': 'Kanishka Misra',
    'author_email': 'kanishka.replies@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kanishkamisra/semantic-memory',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
