# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_business_metrics', 'django_business_metrics.v0']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.1,<5.0', 'prometheus-client>=0.14.1,<0.15.0']

setup_kwargs = {
    'name': 'django-business-metrics',
    'version': '0.1.0a1',
    'description': '',
    'long_description': None,
    'author': 'Reef Technologies',
    'author_email': 'vykintas.baltrusaitis@reef.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
