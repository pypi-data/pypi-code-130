# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetrip']

package_data = \
{'': ['*']}

install_requires = \
['toml>=0.9,<0.10', 'typer>=0.6.1,<0.7.0']

setup_kwargs = {
    'name': 'poetrip',
    'version': '0.1.0',
    'description': 'Generate Pipfile from pyproject.toml',
    'long_description': '\n# Poetrip\n\n[![image](https://img.shields.io/pypi/v/poetrip.svg)](https://pypi.org/project/poetrip/)\n[![image](https://img.shields.io/pypi/l/poetrip.svg)](https://pypi.org/project/poetrip/)\n[![image](https://img.shields.io/pypi/pyversions/poetrip.svg)](https://pypi.org/project/poetrip/)\n\nGenerate Pipfile from pyproject.toml.\n\n## TODO:\n- [x] Basic PyProject to Pipfile conversion\n- [x] Fix scripts appearing in Pipfile\n- [ ] Refactor structure and implement Pipfile to pyproject\n',
    'author': 'Joffrey Bienvenu',
    'author_email': 'joffreybvn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/joffreybvn/poetrip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
