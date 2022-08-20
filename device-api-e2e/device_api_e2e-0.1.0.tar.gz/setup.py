# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['framework',
 'framework.grpc',
 'framework.grpc.clients.google.api',
 'framework.grpc.clients.google.protobuf',
 'framework.grpc.clients.ozonmp.act_device_api.v1',
 'framework.grpc.clients.protoc_gen_openapiv2.options',
 'framework.grpc.clients.validate',
 'framework.rest',
 'framework.sql']

package_data = \
{'': ['*']}

install_requires = \
['PyHamcrest>=2.0.3,<3.0.0',
 'SQLAlchemy>=1.4.40,<2.0.0',
 'allure-pytest>=2.9.45,<3.0.0',
 'allure-python-commons>=2.9.45,<3.0.0',
 'grpcio-tools>=1.47.0,<2.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pytest>=7.1.2,<8.0.0',
 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'device-api-e2e',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'aevtikheev',
    'author_email': 'aevtikheev@ozon.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
