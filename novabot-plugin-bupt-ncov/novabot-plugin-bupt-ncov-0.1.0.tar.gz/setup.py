# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['novabot_plugin_bupt_ncov']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'nonebot2>=2.0.0-beta.5,<3.0.0',
 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'novabot-plugin-bupt-ncov',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'NovaNo1r',
    'author_email': 'mail@novanoir.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
