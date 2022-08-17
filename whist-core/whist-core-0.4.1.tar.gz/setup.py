# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whist_core',
 'whist_core.cards',
 'whist_core.error',
 'whist_core.game',
 'whist_core.scoring',
 'whist_core.session',
 'whist_core.user']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9,<2.0', 'python-jose[cryptography]>=3.3,<4.0']

setup_kwargs = {
    'name': 'whist-core',
    'version': '0.4.1',
    'description': 'Whist rules implementation',
    'long_description': '[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](https://pip.pypa.io/en/stable/?badge=stable)\n[![codecov](https://codecov.io/gh/Whist-Team/Whist-Core/branch/main/graph/badge.svg)](https://codecov.io/gh/Whist-Team/Whist-Core)\n![PyPI](https://img.shields.io/pypi/v/whist-core)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/whist-core)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/whist-core)\n![GitHub repo size](https://img.shields.io/github/repo-size/whist-team/whist-core)\n![Lines of code](https://img.shields.io/tokei/lines/github/whist-team/whist-core)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/whist-core)\n![PyPI - License](https://img.shields.io/pypi/l/whist-core)\n\n# Whist-Core\nWhist rules implementation\n\n## Development\n\n### Setup\nYou need [Poetry](https://python-poetry.org/) for development.\n```bash\n# Create venv and install deps\npoetry install\n```\nThe Python virtual environment will be created in the `.venv` directory.\n\n### Run tests/lint\n```bash\n# Run tests (in venv)\npython -m pytest # or pylint...\n# OR\npoetry run python -m pytest\n```\n\n### Build\nGenerates `sdist` and `bdist_wheel`.\n```bash\npoetry build\n```\n\n### Publish\nYou need the environment variable `POETRY_PYPI_TOKEN_PYPI` filled with a PyPI token.\n```bash\npoetry build\npoetry publish\n# OR\npoetry publish --build\n```\n',
    'author': 'Whist-Team',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Whist-Team/Whist-Core',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
