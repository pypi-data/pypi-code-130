# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_drawer']

package_data = \
{'': ['*']}

install_requires = \
['asyncio>=3.4.3,<4.0.0',
 'httpx>=0.19.0,<0.20.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'pydantic>=1.9.2,<2.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-drawer',
    'version': '0.2.2',
    'description': '适用于 Nonebot2 的AI画画插件(对接文心大模型API)',
    'long_description': '# nonebot-plugin-drawer\n基于文心大模型的AI机器人画画插件。\n\n\n### 通过nb-cli安装（推荐）\nnb plugin install nonebot-plugin-drawer\n### 通过pip安装\n1.pip install nonebot-plugin-drawer 进行安装  \n2.在bot.py添加nonebot.load_plugin(\'nonebot_plugin_drawer\')\n### 配置env.*\n请在env.*配置文件中加入如下两行\n```\nwenxin_ak = "xxxxxxxxxxxxxxxx"\nwenxin_sk = "xxxxxxxxxxxxxxxx"\n```\n文心的ak和sk申请链接：https://wenxin.baidu.com/younger/apiDetail?id=20008\n### 使用方法\n当前支持 "油画", "水彩画", "中国画", 主要擅长风景写意画，请尽量给定比较明确的意象  \n如：油画 江上落日与晚霞\n\n![51addc86ce22c5ff99a12b36cd5834c](https://user-images.githubusercontent.com/35400185/184457437-e22e3f84-69bd-467b-b158-2e3dccce00c1.jpg)\n',
    'author': 'CrazyBoyM',
    'author_email': 'ai-lab@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CrazyBoyM/nonebot-plugin-drawer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
