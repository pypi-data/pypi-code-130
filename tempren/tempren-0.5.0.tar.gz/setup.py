# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tempren', 'tempren.tags', 'tempren.template', 'tempren.template.grammar']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'Unidecode>=1.2.0,<2.0.0',
 'antlr4-python3-runtime>=4.10,<5.0',
 'docstring-parser>=0.13,<0.14',
 'mutagen>=1.45.1,<2.0.0',
 'pathvalidate>=2.4.1,<3.0.0',
 'piexif>=1.1.3,<2.0.0',
 'pymediainfo>=5.1.0,<6.0.0',
 'python-magic>=0.4.27,<0.5.0']

entry_points = \
{'console_scripts': ['tempren = tempren.cli:throwing_main']}

setup_kwargs = {
    'name': 'tempren',
    'version': '0.5.0',
    'description': 'Template-based renaming utility',
    'long_description': '# Tempren - template-based file renaming utility\n\n![run-tests](https://github.com/idle-code/tempren/actions/workflows/run-tests.yml/badge.svg)\n[![codecov](https://codecov.io/gh/idle-code/tempren/branch/develop/graph/badge.svg?token=1CR2PX6GYB)](https://codecov.io/gh/idle-code/tempren)\n[![PyPI version](https://badge.fury.io/py/tempren.svg)](https://badge.fury.io/py/tempren)\n\n`tempren` is a powerful batch file renamer that can generate filenames based on flexible template expressions.\nIt can create new or process existing filenames or sort files into directories based on their attributes (metadata).\n\n**This project is currently in a Work-In-Progress stage so if you are looking for working solution... keep looking.**\n\n## Features\n- Template-based filename/path generation\n- Configurable file selection (filtering)\n- Metadata-based sorting\n\n\n# Quickstart (5 minutes required)\nPeople don\'t have to rename massive amounts of files very often and\nlearning new software just to solve the problem you are facing sporadically\nmight be daunting.\n\nThis quickstart is meant to introduce you to the `tempren` and give you\nenough information to make sure it is up to the task you are facing.\nYou will need around 5 minutes total to work through it.\n\nFor more comprehensive documentation please refer to the [manual](MANUAL.md).\n\n## Install\n```console\n$ pip install [--user] tempren\n```\n\n## Usage\n\n**Note: When playing with tempren make sure to use `--dry-run` (`-d`) flag so that the actual files are not accidentally changed.**\n\nTempren have two main modes of operation: **name** and **path**.\n\nIn the **name** mode (default, enabled by `-n`, `--name` flag), the template is used for filename generation only.\nThis is useful if you want to operate on files specified on the command line or in a single directory.\n\nWith **path** mode (enabled by `-p`, `--path` flag), the template generates a whole path (relative to the input directory).\nThis way you can sort files into dynamically generated catalogues.\n\n### Template syntax\nTag template consists of raw text interleaved with tag invocations.\nEach tag invocation starts with `%` (percent) character followed by tag name, tag configuration (argument) list (enclosed in `()` parentheses) and - optionally -\ntag context (enclosed in `{}` parentheses). Consider following template:\n```tempren\nFile_%Count(start=100).%Lower(){%Ext()}\n```\n\nAbove expression can be split into:\n- Raw text `File_`\n- `Count` tag configured with `start` parameter set to `100`\n- Raw text `.`\n- `Lower` tag (with empty configuration list) operating on context rendered from:\n  - `Ext` tag\n\n**Note: You can use `--list-tags` flag to print tag names provided by your `tempren` version.**\n\nWhen used withing tempren:\n```console\n$ tempren -d "File_%Count(start=100).%Lower(){%Ext()}" test_directory/\n```\nOne may expect results as:\n\n| Input name   | Output name  |\n|--------------|--------------|\n| test.sh      | File_100.sh  |\n| img1.jpg     | File_101.jpg |\n| IMG_1414.jpg | File_102.jpg |\n| document.pdf | File_102.pdf |\n\n\n#### Tag configuration\n#### Pipe list sugar\n### Name mode\n### Path mode\n### Filtering\nTo select which files should be considered for processing one can use filtering predicate.\n\nThere are three types of a filtering expressions supported (by `-ft`, `--filter-type` option):\n- `glob` (default) - filename globbing expression, eg: `*.mp3`, `IMG_????.jpg`\n- `regex` - python-flavored regex, eg: `.*\\.jpe?g`\n- `template` - tag-template evaluated python expression, eg: `%Size() > 10*1024`\n\nSometimes it might be easier to specify filter for files which should **not** be included.\nTo negate/invert filtering expression you can use `-fi`, `--filter-invert` flag.\n\n#### Glob filtering\n#### Regex filtering\n#### Template filtering\n#### Case sensitiveness and filter inversion\nTODO: **IMPLEMENT**\n\nBy default, `glob` and `regex` filtering expressions will match case-sensitive.\nTo allow case-insensitive matching use `-fc`, `--filter-case` flag.\n\n`template` filter isn\'t affected by case-sensitivity flag - you will have to make use of `str.upper` or `str.lower` python methods to simulate that.\n\n### Sorting\n\n## Contribution\nMinimal Python version supported is 3.7, so you should make sure that you have it installed on your system.\nYou can use `pyenv` for that:\n```console\n$ pyenv shell 3.7.10\n```\n\nAfter cloning repo you should install `poetry` as it is used for dependency resolution and packaging:\n```console\n$ pip install [--user] poetry\n```\n\nIt is good to use separate virtualenv for development, `poetry` can spawn one:\n```console\n# Make sure that your `python --version` is at least 3.7 before this step\n$ poetry shell\n```\n\nNow you can install required packages (specified in `pyproject.toml`) via:\n```console\n$ poetry install\n```\n\nCode conventions are enforced via [pre-commit](https://pre-commit.com/). It is listed in development depenencies so if you are able to run tests - you should have it installed too.\nTo get started you will still need to install git hooks:\n```console\n$ pre-commit install\n```\nNow every time you invoke `git commit` a series of cleanup scripts will run and modify your patchset.\n\n### Testing\nTests are written with a help of [pytest](https://docs.pytest.org/en/latest/). Just enter repository root and run:\n```console\n$ pytest\n```\n\n`mypy` on the other hand takes care of static analysis - it can catch early type-related errors:\n```console\n$ mypy\n```\n\n### TODO: Tags development\n',
    'author': 'Paweł Żukowski',
    'author_email': 'p.z.idlecode@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/idle-code/tempren',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
