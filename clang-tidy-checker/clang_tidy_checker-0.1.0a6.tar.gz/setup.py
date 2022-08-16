# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clang_tidy_checker']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'trio>=0.21.0,<0.22.0']

entry_points = \
{'console_scripts': ['clang-tidy-checker = clang_tidy_checker.main:main']}

setup_kwargs = {
    'name': 'clang-tidy-checker',
    'version': '0.1.0a6',
    'description': 'Tool to check C / C++ source codes using clang-tidy.',
    'long_description': '# clang-tidy-checker\n\nTool to check C / C++ source codes using clang-tidy.\n',
    'author': 'Kenta Kabashima',
    'author_email': 'kenta_program37@hotmail.co.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/MusicScience37/clang-tidy-checker',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
