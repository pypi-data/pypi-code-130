# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strawberry_django_dataloaders', 'strawberry_django_dataloaders.core']

package_data = \
{'': ['*']}

install_requires = \
['Django>=3.2', 'strawberry-graphql-django>=0.4,<0.5']

setup_kwargs = {
    'name': 'strawberry-django-dataloaders',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'vojtech',
    'author_email': 'petru.vojtech@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
