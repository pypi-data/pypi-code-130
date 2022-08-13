# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetrip']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.9,<0.10', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['poetrip = poetrip.cli:app']}

setup_kwargs = {
    'name': 'poetrip',
    'version': '1.0.0',
    'description': 'Generate Pipfile from pyproject.toml',
    'long_description': '\n<h1 align="center">Poetrip</h1>\n<p align="center">\n    <em>Generate Pipfile from pyproject.toml.</em>\n</p>\n<p align="center">\n    <a href="https://pypi.org/project/poetrip/" target="_blank">\n        <img src="https://img.shields.io/pypi/v/poetrip.svg" alt="Version">\n    </a>\n    <a href="https://pypi.org/project/poetrip/" target="_blank">\n        <img src="https://img.shields.io/pypi/l/poetrip.svg" alt="License">\n    </a>\n    <a href="https://pypi.org/project/poetrip/" target="_blank">\n        <img src="https://img.shields.io/pypi/pyversions/poetrip.svg" alt="Python">\n    </a>\n</p>\n\n---\n\n**Source Code**: [https://github.com/Joffreybvn/poetrip](https://github.com/Joffreybvn/poetrip)\n\n**Pypi**: [https://pypi.org/project/poetrip/](https://pypi.org/project/poetrip/)\n\n---\n\nPoetrip is a small library and CLI to quickly create Pipfile from existing pyproject.toml.\n\n## Installation\nPoetrip requires Python 3.6 or greater.\n\nUsing **pip**:\n```Shell\npip install poetrip\n```\n\nUsing **poetry**:\n```shell\npoetry add --dev poetrip\n```\n\n## CLI Quickstart\nGet a Pipfile from a pyproject.toml:\n```shell\n$ poetrip --from pyproject.toml --to Pipfile\n```\n\nOr simply:\n```shell\n$ poetrip\n```\nTakes the pyproject.toml in the current folder and generate a Pipfile.\n\n## API Quickstart\nGet a Pipfile from a pyproject.toml:\n```python\nfrom poetrip import PyProject\n\n# Load and transform\npyproject = PyProject.from_file("./pyproject.toml")\npipfile = pyproject.to_pipfile()\n\n# Write to disk\npipfile.to_file("./Pipfile")\n```\n',
    'author': 'Joffrey Bienvenu',
    'author_email': 'joffreybvn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/joffreybvn/poetrip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
