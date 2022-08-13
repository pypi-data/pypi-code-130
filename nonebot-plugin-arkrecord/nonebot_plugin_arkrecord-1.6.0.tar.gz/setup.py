# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_arkrecord', 'nonebot_plugin_arkrecord.ark']

package_data = \
{'': ['*'],
 'nonebot_plugin_arkrecord': ['res_file/output_csv/*',
                              'res_file/record_image/*',
                              'resource/*',
                              'resource/images/*',
                              'resource/profile/*',
                              'resource/ttf/*']}

install_requires = \
['Pillow',
 'XlsxWriter',
 'lxml',
 'matplotlib',
 'nonebot-adapter-onebot>=2.0.0b1,<3.0.0',
 'nonebot2>=2.0.0b4,<3.0.0',
 'requests']

setup_kwargs = {
    'name': 'nonebot-plugin-arkrecord',
    'version': '1.6.0',
    'description': 'Nonebot plugin for fetching and analyzing gacha records of arknights',
    'long_description': '<h1 align="center"><b>nonebot_plugin_arkrecord</b></h1>\n<p align="center">\n    <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="python">\n    <img src="https://img.shields.io/badge/Nonebot-2.0.0b4-green" alt="python">\n    <img src="https://img.shields.io/badge/Onebot-11-blue" alt="python">\n</p>\n<h2 align="center"><b>欢迎使用明日方舟抽卡分析NoneBot2插件!</b></h2>\n<h4 align="center">本插件为基于python3.9开发的NoneBot2插件，NoneBot2适配器为OneBotV11，当前版本V1.6.0\n</h4>\n\n## **丨插件部署说明**\n\n如果你还没有安装NoneBot2，可以参考[NoneBot2官网](https://nb2.baka.icu/)配置NoneBot2后再安装本插件\n\n本插件依赖于sqlite数据库，参考网络资源（如[菜鸟教程](https://www.runoob.com/sqlite/sqlite-installation.html)）安装SQLite数据库并设置环境变量（windows）后即可，无需配置数据库环境\n\n输出时，如果没有可用干员头像，将以海猫头像代替\n\n\n\n\n## **丨插件部署方法**\n\n在命令行（cmd）中\n\n``` shell\npip install nonebot_plugin_arkrecord\n```\n\n载入插件方式与载入其他插件方式相同，即在NoneBot2的`bot.py`中添加一行\n\n```python\nnonebot.load_plugin(\'nonebot_plugin_arkrecord\')\n```\n\n## **丨插件使用方法**\n### **token设置**\n\n每个用户第一次使用时，需要设置token。\n\n**token获取方法**：在官网登录后，根据你的服务器，选择复制以下网址中的内容\n \n官服：https://as.hypergryph.com/user/info/v1/token_by_cookie\n\nB服：https://web-api.hypergryph.com/account/info/ak-b\n\n***请在浏览器中获取token，避免在QQ打开的网页中获取，否则可能获取无效token***\n\n**token设置方法**：使用插件命令`方舟抽卡token 你的token`(自动识别B服、官服token)\n或`方舟寻访token 你的token`进行设置\n\n如网页中内容为\n```json\n{"status":0,"msg":"OK","data":{"token":"example123456789"}}\n```\n则使用命令 `方舟抽卡token example123456789`， 如果间隔超**3天**再次使用，建议重新使用上述方式设置token\n### **寻访记录分析**\n\n设置token后，直接使用`方舟抽卡分析`或`方舟寻访分析`即可\n\n还可以使用`方舟抽卡分析 数字`，分析最近一定抽数的寻访情况\n\n如`方舟抽卡分析 100`分析最近100抽的情况\n\n![示例输出](./nonebot_plugin_arkrecord/res_file/record_image/record_img_870599048.png)\n\n### **更新卡池信息与干员头像**\n\n使用`方舟卡池更新`命令，自动从PRTS更新卡池信息及干员头像文件\n\n### **导出记录**\n\n使用`方舟抽卡导出`命令，可以在群聊中导出你当前关联token的储存于插件数据库中的寻访记录。请注意，目前只支持在群聊中导出\n\n### **获取帮助**\n使用`方舟寻访帮助`或`方舟抽卡帮助`命令，可以获取插件帮助\n\n### **其他功能**\n使用`随机干员`命令，随机给出一张干员头像\n\n## **丨更新日志**\n\n- V1.6.0 修复了卡池更新后必须重新启动才能获取更新后卡池信息的bug\n- V1.6.0 数据库文件不再存放在```/resource```，迁移至 ```C://USERS/{USER_NAME}/.arkrecord```(Windows),```/root/.arkrecord```(Linux)存放。\n\n## **丨参考**\n作图代码参考于\n\n- [nonebot-plugin-gachalogs](https://github.com/monsterxcn/nonebot-plugin-gachalogs)\n\n- [nonebot_plugin_gamedraw](https://github.com/HibiKier/nonebot_plugin_gamedraw)\n\n## **丨开发人员信息**\n主体开发[本人](https://github.com/zheuziihau)\n\n美术资源及需求设计 [@Alnas1](https://github.com/Alnas1)',
    'author': 'kwtk',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zheuziihau',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
