# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '..'}

modules = \
['__init__']
install_requires = \
['httpx>=0.23.0', 'nonebot2>=2.0.0-beta.1,<3.0.0']

extras_require = \
{'onebot': ['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0']}

setup_kwargs = {
    'name': 'nonebot-plugin-moegoe',
    'version': '0.5.0',
    'description': '日韩中 VITS 模型拟声',
    'long_description': '<!--\n * @Author         : yiyuiii\n * @Date           : 2020-8-20 22:30:00\n * @LastEditors    : yiyuiii\n * @LastEditTime   : 2020-8-20 22:30:00\n * @Description    : None\n * @GitHub         : https://github.com/yiyuiii\n-->\n\n<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# nonebot-plugin-moegoe\n\n_✨ 日韩中 VITS 模型拟声 by fumiama✨_\n\n搬运自ZeroBot-Plugin仓库：https://github.com/FloatTech/ZeroBot-Plugin/tree/master/plugin/moegoe\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/cscs181/QQ-Github-Bot/master/LICENSE">\n    <img src="https://img.shields.io/github/license/cscs181/QQ-Github-Bot.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-status">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-status.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n\n**在聊天中输入:**\n\n- 让[宁宁|爱瑠|芳乃|茉子|丛雨|小春|七海]说日语：(日语)\n- 让[Sua|Mimiru|Arin|Yeonhwa|Yuhwa|Seonbae]说韩语：(韩语)\n- 让[派蒙|凯亚|安柏|丽莎|琴|香菱|枫原万叶|迪卢克|温迪|可莉|早柚|托马|芭芭拉|优菈|云堇|钟离|魈|凝光|雷电将军|北斗|甘雨|七七|刻晴|神里绫华|雷泽|神里绫人|罗莎莉亚|阿贝多|八重神子|宵宫|荒泷一斗|九条裟罗|夜兰|珊瑚宫心海|五郎|达达利亚|莫娜|班尼特|申鹤|行秋|烟绯|久岐忍|辛焱|砂糖|胡桃|重云|菲谢尔|诺艾尔|迪奥娜|鹿野院平藏]说中文：(中文)\n\n**Bot返回语音**',
    'author': 'yiyuiii',
    'author_email': 'yiyuiii@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yiyuiii/nonebot-plugin-moegoe',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
