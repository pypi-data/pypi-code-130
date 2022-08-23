# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['moka_python_sdk',
 'moka_python_sdk.models',
 'moka_python_sdk.models.library',
 'moka_python_sdk.models.library.entity',
 'moka_python_sdk.models.merchant',
 'moka_python_sdk.models.merchant.entity',
 'moka_python_sdk.models.oauth',
 'moka_python_sdk.models.oauth.entity',
 'moka_python_sdk.models.oauth.subscription',
 'moka_python_sdk.models.oauth.subscription.entity',
 'moka_python_sdk.models.report',
 'moka_python_sdk.models.report.entity',
 'moka_python_sdk.models.transaction',
 'moka_python_sdk.models.transaction.bill',
 'moka_python_sdk.models.transaction.bill.entity',
 'moka_python_sdk.models.transaction.entity',
 'moka_python_sdk.models.transaction.invoice',
 'moka_python_sdk.models.transaction.invoice.entity',
 'moka_python_sdk.models.transaction.order',
 'moka_python_sdk.models.transaction.order.entity',
 'moka_python_sdk.network']

package_data = \
{'': ['*']}

install_requires = \
['dacite>=1.6.0,<2.0.0', 'pyhumps>=3.7.2,<4.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'moka-python-sdk',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'LandX Engineering',
    'author_email': 'tech@landx.id',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
