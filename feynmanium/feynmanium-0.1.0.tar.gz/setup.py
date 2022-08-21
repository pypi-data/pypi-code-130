# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['feynmanium', 'feynmanium.cogs']

package_data = \
{'': ['*']}

install_requires = \
['CairoSVG>=2.5.2,<3.0.0',
 'chess>=1.9.2,<2.0.0',
 'discord.py>=2.0.0,<3.0.0',
 'googletrans-py>=4.0.0,<5.0.0',
 'mpmath>=1.2.1,<2.0.0',
 'sympy>=1.10.1,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'tomlkit>=0.11.4,<0.12.0',
 'uvloop>=0.16.0,<0.17.0']

entry_points = \
{'console_scripts': ['feynmanium = feynmanium.run:main']}

setup_kwargs = {
    'name': 'feynmanium',
    'version': '0.1.0',
    'description': 'A discord bot that works.',
    'long_description': '##########\nFeynmanium\n##########\n\n|Codacy Badge| |pre-commit.ci status| |Total alerts| |Language grade: Python| |Code style: black|\n\nA `Discord`_ bot that works.\n\n************\nRequirements\n************\n\nFeynmanium requires:\n\n-  `Python`_ v3.10 or later\n-  `Poetry`_ v1.1 or later\n\n************\nInstallation\n************\n\nRun the following commands to install Feynmanium:\n\n::\n\n   git clone https://github.com/tb148/feynmanium.git\n   poetry install\n\n*****\nUsage\n*****\n\nRun the following commmand to run Feynmanium\n\n::\n\n   python -m feynmanium <token>\n\n.. _Discord: https://discord.com/\n.. _Python: https://python.org/\n.. _Poetry: https://python-poetry.org/\n\n.. |Codacy Badge| image:: https://app.codacy.com/project/badge/Grade/3f036df7eb36457d8182c08085e42953\n   :target: https://www.codacy.com/gh/tb148/feynmanium/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tb148/feynmanium&amp;utm_campaign=Badge_Grade\n.. |pre-commit.ci status| image:: https://results.pre-commit.ci/badge/github/tb148/feynmanium/trunk.svg\n   :target: https://results.pre-commit.ci/latest/github/tb148/feynmanium/trunk\n.. |Total alerts| image:: https://img.shields.io/lgtm/alerts/g/tb148/feynmanium.svg?logo=lgtm&logoWidth=18\n   :target: https://lgtm.com/projects/g/tb148/feynmanium/alerts/\n.. |Language grade: Python| image:: https://img.shields.io/lgtm/grade/python/g/tb148/feynmanium.svg?logo=lgtm&logoWidth=18\n   :target: https://lgtm.com/projects/g/tb148/feynmanium/context:python\n.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black',
    'author': 'Tony Brown',
    'author_email': 'tb148@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tb148/feynmanium',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
