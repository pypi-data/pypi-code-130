# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gh_folder_download']

package_data = \
{'': ['*']}

install_requires = \
['PyGithub>=1.55,<2.0', 'typer[all]>=0.6.1,<0.7.0', 'wget>=3.2,<4.0']

entry_points = \
{'console_scripts': ['gh-folder-download = gh_folder_download.main:app']}

setup_kwargs = {
    'name': 'gh-folder-download',
    'version': '0.1.0',
    'description': 'A command line application (CLI) to download only a specific folder without downloading the full repository implemented with Python using Typer and GitHub API.',
    'long_description': '# GitHub Folder Downloader\n\n[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)\n[![Version](https://img.shields.io/pypi/v/gh-folder-download?color=%2334D058&label=Version)](https://pypi.org/project/gh-folder-download)\n[![Last commit](https://img.shields.io/github/last-commit/leynier/gh-folder-download.svg?style=flat)](https://github.com/leynier/gh-folder-download/commits)\n[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/leynier/gh-folder-download)](https://github.com/leynier/gh-folder-download/commits)\n[![Github Stars](https://img.shields.io/github/stars/leynier/gh-folder-download?style=flat&logo=github)](https://github.com/leynier/gh-folder-download/stargazers)\n[![Github Forks](https://img.shields.io/github/forks/leynier/gh-folder-download?style=flat&logo=github)](https://github.com/leynier/gh-folder-download/network/members)\n[![Github Watchers](https://img.shields.io/github/watchers/leynier/gh-folder-download?style=flat&logo=github)](https://github.com/leynier/gh-folder-download)\n[![GitHub contributors](https://img.shields.io/github/contributors/leynier/gh-folder-download)](https://github.com/leynier/gh-folder-download/graphs/contributors)\n\nA command line application (CLI) to download only a specific folder without downloading the full repository implemented with Python using Typer and GitHub API.\n\n```bash\nUsage: gh-folder-download [OPTIONS]\n\nOptions:\n  --url TEXT                      Repository URL  [required]\n  --output DIRECTORY              Output folder  [default: .]\n  --token TEXT                    GitHub token\n  --force / --no-force            Remove existing output folder if it exists\n                                  [default: no-force]\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n  --help                          Show this message and exit.\n```\n',
    'author': 'Leynier Gutiérrez González',
    'author_email': 'leynier41@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/leynier/gh-folder-download',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
