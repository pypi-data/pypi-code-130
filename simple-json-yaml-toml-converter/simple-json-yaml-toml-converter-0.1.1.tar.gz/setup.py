# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simple_json_yaml_toml_converter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.1.3,<9.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['simple-json-yaml-toml-converter = '
                     'simple_json_yaml_toml_converter.cli:command']}

setup_kwargs = {
    'name': 'simple-json-yaml-toml-converter',
    'version': '0.1.1',
    'description': 'Simple json/yaml/toml CLI converter.',
    'long_description': '![PyPI](https://img.shields.io/pypi/v/simple-json-yaml-toml-converter)\n![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/0djentd/simple-json-yaml-toml-converter?include_prereleases)\n![GitHub all releases](https://img.shields.io/github/downloads/0djentd/simple-json-yaml-toml-converter/total)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simple-json-yaml-toml-converter)\n\n![GitHub issues](https://img.shields.io/github/issues/0djentd/simple-json-yaml-toml-converter)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/0djentd/simple-json-yaml-toml-converter)\n![GitHub Repo stars](https://img.shields.io/github/stars/0djentd/simple-json-yaml-toml-converter?style=social)\n\n# simple-json-yaml-toml-converter\n## Description\nSimple json/yaml/toml converter.\n\n## How to use\n```\nUsage: simple-json-yaml-toml-converter [OPTIONS] [INPUT_FILES]...\n\nOptions:\n  -o, --output-format TEXT\n  --debug / --no-debug\n  -e, --encoding TEXT\n  --help                    Show this message and exit.\n```\n',
    'author': '0djentd',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/0djentd/simple-json-yaml-toml-converter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
