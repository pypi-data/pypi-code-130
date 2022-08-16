# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snatch', 'snatch.base', 'snatch.helpers']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=13.11.1,<14.0.0',
 'arrow',
 'asbool',
 'boto3',
 'jupyter>=1.0.0,<2.0.0',
 'loguru',
 'marshmallow-enum>=1.5.1,<2.0.0',
 'marshmallow>=3.15.0,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'python-dotenv',
 'requests>=2.27.1,<3.0.0',
 'scalpl',
 'typing-extensions>=4.2.0,<5.0.0',
 'validate-docbr']

setup_kwargs = {
    'name': 'py-snatch',
    'version': '2.26.0',
    'description': "The Friendly Integration Library for Data Scientists. Don't You Just Know It?",
    'long_description': None,
    'author': 'A55 Tech',
    'author_email': 'tech@a55.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
