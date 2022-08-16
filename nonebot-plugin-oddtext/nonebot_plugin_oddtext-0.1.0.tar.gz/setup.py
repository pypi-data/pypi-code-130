# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_oddtext']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.0.0-beta.4,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-oddtext',
    'version': '0.1.0',
    'description': 'Nonebot2 插件，用于抽象话等文字生成',
    'long_description': '# nonebot-plugin-oddtext\n\n[Nonebot2](https://github.com/nonebot/nonebot2) 插件，用于抽象话等文字生成\n\n\n### 安装\n\n- 使用 nb-cli\n\n```\nnb plugin install nonebot_plugin_oddtext\n```\n\n- 使用 pip\n\n```\npip install nonebot_plugin_oddtext\n```\n\n\n### 使用\n\n**以下命令需要加[命令前缀](https://v2.nonebot.dev/docs/api/config#Config-command_start) (默认为`/`)，可自行设置为空**\n\n```\n指令 + 文本\n```\n\n#### 支持的指令\n\n - 抽象话\n\n> 抽象话 测试一下\n\n<img src="https://s2.loli.net/2022/08/16/z3b2OKMstpumlgB.png" width="100" />\n\n\n - 火星文\n\n> 火星文 测试一下\n    \n```\n測試①丅\n```\n\n\n - 蚂蚁文\n\n> 蚂蚁文 测试一下\n\n<img src="https://s2.loli.net/2022/08/16/WKrxAC95oUIgvYO.png" width="100" />\n\n\n - 翻转文字（仅支持英文）\n\n> 翻转文字 test\n    \n```\nʇsǝʇ\n```\n\n\n - 故障文字\n\n> 故障文字 测试一下\n\n<img src="https://s2.loli.net/2022/08/16/ITACcLfarNuF3GZ.png" width="100" />\n',
    'author': 'meetwq',
    'author_email': 'meetwq@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/noneplugin/nonebot-plugin-oddtext',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
