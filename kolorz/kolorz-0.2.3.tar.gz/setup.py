# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kolorz']

package_data = \
{'': ['*']}

install_requires = \
['dotwiz>=0.3.1,<0.4.0']

entry_points = \
{'console_scripts': ['kolorz = kolorz.cli:kolor']}

setup_kwargs = {
    'name': 'kolorz',
    'version': '0.2.3',
    'description': 'A fast, extensible, and kolorful python library to print colored output to the terminal',
    'long_description': '<h2 align="center"> ━━━━━━  ❖  ━━━━━━ </h2>\n\n<!-- BADGES -->\n<div align="center">\n   <p></p>\n   \n   <img src="https://img.shields.io/github/stars/dotzenith/kolorz?color=F8BD96&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/forks/dotzenith/kolorz?color=DDB6F2&labelColor=302D41&style=for-the-badge">   \n\n   <img src="https://img.shields.io/github/repo-size/dotzenith/kolorz?color=ABE9B3&labelColor=302D41&style=for-the-badge">\n   \n   <img src="https://img.shields.io/github/commit-activity/y/dotzenith/kolorz?color=96CDFB&labelColor=302D41&style=for-the-badge&label=COMMITS"/>\n   <br>\n</div>\n\n<p/>\n\n---\n\n### ❖ Information \n\n  kolorz is a simple, fast, and extensible python library to facilitate printing colors to terminals that support true color  \n\n  <img src="https://github.com/dotzenith/dotzenith/blob/main/assets/kolorz/kolorz.png" alt="kolorz">\n\n---\n\n### ❖ Installation\n\n> Install from pip\n```sh\npip3 install kolorz\n```\n\n> Install from source\n- First, install [poetry](https://python-poetry.org/)\n```sh\ngit clone https://github.com/dotzenith/kolorz.git\ncd kolorz\npoetry build\npip3 install ./dist/kolorz-0.2.3.tar.gz\n```\n\n### ❖ Usage \n\nUsing the kolorz CLI endpoint to print out all available colorschemes:  \n\n```\n$ kolorz\nSupported colorschemes: \n\ncatppuccin latte\ncatppuccin frappe\ncatppuccin macchiato\ncatppuccin mocha\ndracula\nnord\ngruvbox\nonedark\ntokyonight\nayu\npalenight\ngogh\n```\n\nUsing the kolorz python interface to print colored output:\n\n```python\nfrom kolorz import make_kolorz\n\nkl = make_kolorz()\n\nprint(f"{kl.blue}This is some{kl.end} {kl.orange}output{kl.end}")\n```\n\nThe following colors are available, but more can be added (more on that later):\n```\nred\npurple\nblue\ngreen\norange\nyellow\nwhite\n```\n\nBy default, the colorscheme is set to `catppuccin mocha` but that can be changed to any of the colorschemes listed by `kolorz`. For example:\n\n```python\nfrom kolorz import make_kolorz\n\nkl = make_kolorz("nord")\n\nprint(f"{kl.blue}This is some{kl.end} {kl.orange}output{kl.end}")\n```\n\nUsers can also define their own colorschemes:\n\n```python\nfrom kolorz import kolorz\n\nnew_colors = {\n    "red": (210, 15, 57),\n    "purple": (136, 57, 239),\n    "blue": (30, 102, 245),\n    "green": (64, 160, 43),\n    "orange": (254, 100, 11),\n    "yellow": (223, 142, 29),\n    "white": (204, 208, 218),\n}\n\nkl = make_kolorz(custom=new_colors)\n\nprint(f"{kl.blue}This is some{kl.end} {kl.orange}output{kl.end}")\n```\n\n> When adding a custom colorscheme, the user is not restricted to just seven colors. The user can define as many colors as they\'d like in the dict structure\n\nAdding or overriding a color\n\n```python\nfrom kolorz import make_kolorz, make_kolor\n\nkl = make_kolorz()\n\n# Adding\nkl.rosewater = make_kolor((245, 224, 220))\n\n# Overriding\nkl.blue = make_kolor((137, 220, 235))\n\nprint(f"{kl.rosewater}This is some{kl.end} {kl.blue}output{kl.end}")\n```\n\n---\n\n### ❖ What\'s New? \n0.2.3 - Added the ability to use numbered colors instead of named colors\n\n---\n\n<div align="center">\n\n   <img src="https://img.shields.io/static/v1.svg?label=License&message=MIT&color=F5E0DC&labelColor=302D41&style=for-the-badge">\n\n</div>\n',
    'author': 'dotzenith',
    'author_email': 'contact@danshu.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
