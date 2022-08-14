# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wagtail_qrcode',
 'wagtail_qrcode.test',
 'wagtail_qrcode.test.migrations',
 'wagtail_qrcode.test.tests']

package_data = \
{'': ['*'], 'wagtail_qrcode': ['templates/wagtail_qrcode/admin/*']}

install_requires = \
['PyQRCode>=1.2.1,<2.0.0', 'wagtail>=2.15']

entry_points = \
{'console_scripts': ['clean = scripts:clean',
                     'develop = scripts:develop',
                     'test-scripts = scripts:test_scripts']}

setup_kwargs = {
    'name': 'wagtail-qrcode',
    'version': '0.1.3',
    'description': 'Create a QR code that can be used to link to a wagtail page',
    'long_description': None,
    'author': 'Nick Moreton',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nickmoreton/wagtail-qrcode',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
