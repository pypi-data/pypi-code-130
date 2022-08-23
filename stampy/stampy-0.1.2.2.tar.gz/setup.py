# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stampy']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0', 'click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['stampy = stampy.main:main']}

setup_kwargs = {
    'name': 'stampy',
    'version': '0.1.2.2',
    'description': '４文字の文字列をスタンプ風画像に変換するツール ',
    'long_description': '<div align="center">\n\n![Last commit](https://img.shields.io/github/last-commit/Comamoca/stampy?style=flat-square)\n![Repository Stars](https://img.shields.io/github/stars/Comamoca/stampy?style=flat-square)\n![Issues](https://img.shields.io/github/issues/Comamoca/stampy?style=flat-square)\n![Open Issues](https://img.shields.io/github/issues-raw/Comamoca/stampy?style=flat-square)\n![Bug Issues](https://img.shields.io/github/issues/Comamoca/stampy/bug?style=flat-square)\n\n#  stampy 🍣\n\n４文字の文字列をスタンプ風の画像に変換します。\n\n![生成出来る画像の例](./out.png "生成出来る画像の例")\n\n</div>\n\n<table>\n  <thead>\n    <tr>\n      <th style="text-align:center">🍡日本語</th>\n      <th style="text-align:center">🍔Sorry, Japanease Only</th>\n    </tr>\n  </thead>\n</table>\n\n<div align="center">\n\n</div>\n\n## 🚀 使い方\n\n```\n# 文字列を与えるとスタンプ風の画像を生成します。\nstampy にんにん\n\n# オプションで色(RGB)を指定する事ができます。\nstampy にんにん --color 100,180,123\n\n# ４文字以外の文字列はエラーになります。\nstampy にゃんにゃん\n\n# カレントディレクトリにoutput.pngという画像が出力されます。\n```\n\n## ⬇️  Install\n\n```sh\n# PyPIからでもインストール出来ます。\npipx install stampy\n\n# インストールにはpipxを推奨します。\npipx install git+https://github.com/Comamoca/stampy\n```\n\n## ⛏️   開発\n\n```sh\ngit clone https://github.com/Comamoca/stampy\ncd stampy\npoetry install\npoetry run python src/main.py\n```\n## 📝 Todo\n\nNot yet...:zzz:\n\n## 📜 ライセンス\n\nMIT\n[SIL Open Font License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL_web)\n\n### 🧩 Modules\n\n[💕 スペシャルサンクス](#💕スペシャルサンクス)\n\n## 👏 影響を受けたプロジェクト\n\nNot yet...:zzz:\n\n## 💕 スペシャルサンクス\n\n- [M+フォント](https://mplusfonts.github.io/)\n\n- [pillow](https://github.com/python-pillow/Pillow)\n\n- [click](https://github.com/pallets/click)\n',
    'author': 'Comamoca',
    'author_email': 'comamoca.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
