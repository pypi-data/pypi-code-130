# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_drawer']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0',
 'httpx>=0.23.0,<0.24.0',
 'nonebot>=1.9.1,<2.0.0',
 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-drawer',
    'version': '0.2.0',
    'description': '适用于 Nonebot2 的AI画画插件(对接文心大模型API)',
    'long_description': None,
    'author': 'CrazyBoyM',
    'author_email': 'ai-lab@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
