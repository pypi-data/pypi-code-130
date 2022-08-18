# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_xml']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.70.0', 'pydantic>=1.9.0', 'xsdata>=22.1']

setup_kwargs = {
    'name': 'fastapi-xml',
    'version': '1.0.0a2',
    'description': 'adds xml support to fastapi',
    'long_description': 'None',
    'author': 'Leon Rendel',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
