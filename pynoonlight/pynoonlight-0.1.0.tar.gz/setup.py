# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pynoonlight']

package_data = \
{'': ['*']}

install_requires = \
['mkdocstrings-python>=0.7.1,<0.8.0',
 'pychalk==2.0.1',
 'pydantic>=1.9.2,<2.0.0',
 'requests>=2.28.1,<3.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'tzlocal>=4.2,<5.0',
 'validators>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'pynoonlight',
    'version': '0.1.0',
    'description': 'Create and update alarms for Noonlight',
    'long_description': "# pynoonlight\n\n[![Test](https://github.com/IceBotYT/pynoonlight/actions/workflows/test.yml/badge.svg)](https://github.com/IceBotYT/pynoonlight/actions/workflows/test.yml)\n[![PyPI](https://img.shields.io/pypi/v/pynoonlight?style=flat-square)](https://pypi.python.org/pypi/pynoonlight/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pynoonlight?style=flat-square)](https://pypi.python.org/pypi/pynoonlight/)\n[![PyPI - License](https://img.shields.io/pypi/l/pynoonlight?style=flat-square)](https://pypi.python.org/pypi/pynoonlight/)\n[![codecov](https://codecov.io/gh/IceBotYT/pynoonlight/branch/main/graph/badge.svg?token=C235MUQANU)](https://codecov.io/gh/IceBotYT/pynoonlight)\n[![Coookiecutter - Wolt](https://img.shields.io/badge/cookiecutter-Wolt-00c2e8?style=flat-square&logo=cookiecutter&logoColor=D4AA00&link=https://github.com/woltapp/wolt-python-package-cookiecutter)](https://github.com/woltapp/wolt-python-package-cookiecutter)\n\n\n---\n\n**Documentation**: [https://IceBotYT.github.io/pynoonlight](https://IceBotYT.github.io/pynoonlight)\n\n**Source Code**: [https://github.com/IceBotYT/pynoonlight](https://github.com/IceBotYT/pynoonlight)\n\n**PyPI**: [https://pypi.org/project/pynoonlight/](https://pypi.org/project/pynoonlight/)\n\n---\n\nCreate and update alarms for Noonlight\n\n## Installation\n\n```sh\npip install pynoonlight\n```\n\n## Development\n\n* Clone this repository\n* Requirements:\n  * [Poetry](https://python-poetry.org/)\n  * Python 3.7\n  * Python 3.10\n\n* Setup virtual environments\n\nThis will modify your `.bashrc` file to create two new aliases to point to the virtual environments.\nThe two new aliases are:\n- noonlight_python3.10\n- noonlight_python3.7\n\n```sh\ncd pynoonlight\nchmod +x setup_virtual_environments.sh\n./setup_virtual_environments.sh\n```\n\n* Activate the virtual environment (Python 3.10)\n\n```sh\nnoonlight_python3.10\n```\n\n* Activate the virtual environment (Python 3.7)\n```sh\nnoonlight_python3.7\n```\n\n### Testing\n\n```sh\npytest\n```\n\n### Documentation\n\nThe documentation is automatically generated from the content of the [docs directory](./docs) and from the docstrings\n of the public signatures of the source code. The documentation is updated and published as a [Github project page\n ](https://pages.github.com/) automatically as part each release.\n\n### Releasing\n\nTrigger the [Draft release workflow](https://github.com/IceBotYT/pynoonlight/actions/workflows/draft_release.yml)\n(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.\n\nFind the draft release from the\n[GitHub releases](https://github.com/IceBotYT/pynoonlight/releases) and publish it. When\n a release is published, it'll trigger [release](https://github.com/IceBotYT/pynoonlight/blob/master/.github/workflows/release.yml) workflow which creates PyPI\n release and deploys updated documentation.\n\n### Pre-commit\n\nPre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality\n checks to make sure the changeset is in good shape before a commit/push happens.\n\nYou can install the hooks with (runs for each commit):\n\n```sh\npre-commit install\n```\n\nOr if you want them to run only for each push:\n\n```sh\npre-commit install -t pre-push\n```\n\nOr if you want e.g. want to run all checks manually for all files:\n\n```sh\npre-commit run --all-files\n```\n\n---\n\nThis project was generated using the [wolt-python-package-cookiecutter](https://github.com/woltapp/wolt-python-package-cookiecutter) template.\n",
    'author': 'IceBotYT',
    'author_email': 'icebotyt@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://IceBotYT.github.io/pynoonlight',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
