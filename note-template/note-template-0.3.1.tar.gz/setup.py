# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['note_template']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.4,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'pydantic>=1.9.2,<2.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['note-template = note_template.cli:commands']}

setup_kwargs = {
    'name': 'note-template',
    'version': '0.3.1',
    'description': '',
    'long_description': '![PyPI](https://img.shields.io/pypi/v/note-template)\n![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/0djentd/note-template?include_prereleases)\n![GitHub all releases](https://img.shields.io/github/downloads/0djentd/note-template/total)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/note-template)\n\n![GitHub issues](https://img.shields.io/github/issues/0djentd/note-template)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/0djentd/note-template)\n![GitHub Repo stars](https://img.shields.io/github/stars/0djentd/note-template?style=social)\n\n[![Python package](https://github.com/0djentd/note-template/actions/workflows/python-package.yml/badge.svg)](https://github.com/0djentd/note-template/actions/workflows/python-package.yml)\n[![Pylint](https://github.com/0djentd/note-template/actions/workflows/pylint.yml/badge.svg)](https://github.com/0djentd/note-template/actions/workflows/pylint.yml)\n\n# note-template\n## Description\nSimple CLI tool to create notes using templates.\n\n## How to use\n```\nUsage: note-template [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --data-dir TEXT                 Data directory.\n  --config-dir TEXT               Config directory.\n  --cache-dir TEXT                Cache directory.\n  --state-dir TEXT                State directory.\n  --log-dir TEXT                  Log directory.\n  --verbose / --no-verbose        Show additional information.\n  --debug / --no-debug            Show debug information.\n  --templates-dir TEXT            Templates directory.\n  --notes-dir TEXT                Notes directory.\n  --editor TEXT                   Text editor.\n  --create-default-directories BOOLEAN\n  --dont-save-note-if-no-changes BOOLEAN\n  --help                          Show this message and exit.\n\nCommands:\n  config\n  new\n  templates\n```\n',
    'author': '0djentd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/0djentd/note-template',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
