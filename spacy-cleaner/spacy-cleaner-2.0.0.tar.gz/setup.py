# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spacy_cleaner']

package_data = \
{'': ['*']}

install_requires = \
['spacy>=3.4.1,<3.5.0']

entry_points = \
{'console_scripts': ['spacy-cleaner = spacy_cleaner.__main__:app']}

setup_kwargs = {
    'name': 'spacy-cleaner',
    'version': '2.0.0',
    'description': 'Easily clean text with spaCy!',
    'long_description': '# spacy-cleaner\n\n<div align="center">\n\n[![Build status](https://github.com/Ce11an/spacy-cleaner/workflows/build/badge.svg?branch=main&event=push)](https://github.com/Ce11an/spacy-cleaner/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/spacy-cleaner.svg)](https://pypi.org/project/spacy-cleaner/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/Ce11an/spacy-cleaner/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/Ce11an/spacy-cleaner/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/Ce11an/spacy-cleaner/releases)\n[![License](https://img.shields.io/github/license/Ce11an/spacy-cleaner)](https://github.com/Ce11an/spacy-cleaner/blob/main/LICENSE)\n[![codecov](https://codecov.io/gh/Ce11an/spacy-cleaner/branch/main/graph/badge.svg?token=H28KHYYFHX)](https://codecov.io/gh/Ce11an/spacy-cleaner)\n[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Ce11an_spacy-cleaner&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Ce11an_spacy-cleaner)\n\nEasily clean text with spaCy!\n\n</div>\n\n## Installation\n\n```bash\npip install -U spacy-cleaner\n```\n\nor install with `Poetry`\n\n```bash\npoetry add spacy-cleaner\n```\n\n### Makefile usage\n\n[`Makefile`](https://github.com/Ce11an/spacy-cleaner/blob/main/Makefile) contains a lot of functions for faster development.\n\n<details>\n<summary>1. Download and remove Poetry</summary>\n<p>\n\nTo download and install Poetry run:\n\n```bash\nmake poetry-download\n```\n\nTo uninstall\n\n```bash\nmake poetry-remove\n```\n\n</p>\n</details>\n\n<details>\n<summary>2. Install all dependencies and pre-commit hooks</summary>\n<p>\n\nInstall requirements:\n\n```bash\nmake install\n```\n\nPre-commit hooks can be installed after `git init` via\n\n```bash\nmake pre-commit-install\n```\n\n</p>\n</details>\n\n<details>\n<summary>3. Codestyle</summary>\n<p>\n\nAutomatic formatting uses `pyupgrade`, `isort` and `black`.\n\n```bash\nmake codestyle\n\n# or use synonym\nmake formatting\n```\n\nCodestyle checks only, without rewriting files:\n\n```bash\nmake check-codestyle\n```\n\n> Note: `check-codestyle` uses `isort`, `black` and `darglint` library\n\nUpdate all dev libraries to the latest version using one command\n\n```bash\nmake update-dev-deps\n```\n\n<details>\n<summary>4. Code security</summary>\n<p>\n\n```bash\nmake check-safety\n```\n\nThis command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.\n\n```bash\nmake check-safety\n```\n\n</details>\n<p>\n\n</p>\n</details>\n\n<details>\n<summary>4. Type checks</summary>\n<p>\n\nRun `mypy` static type checker\n\n```bash\nmake mypy\n```\n\n</p>\n</details>\n\n<details>\n<summary>5. Tests with coverage badges</summary>\n<p>\n\nRun `pytest`\n\n```bash\nmake test\n```\n\n</p>\n</details>\n\n<details>\n<summary>6. All linters</summary>\n<p>\n\nOf course there is a command to ~~rule~~ run all linters in one:\n\n```bash\nmake lint\n```\n\nthe same as:\n\n```bash\nmake test && make check-codestyle && make mypy && make check-safety\n```\n\n</p>\n</details>\n\n<details>\n<summary>7. Cleanup</summary>\n<p>\nDelete pycache files\n\n```bash\nmake pycache-remove\n```\n\nRemove package build\n\n```bash\nmake build-remove\n```\n\nDelete .DS_STORE files\n\n```bash\nmake dsstore-remove\n```\n\nRemove .mypy_cache\n\n```bash\nmake mypycache-remove\n```\n\nOr to remove all above run:\n\n```bash\nmake cleanup\n```\n\n</p>\n</details>\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/Ce11an/spacy-cleaner/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n### List of labels and corresponding titles\n\n|               **Label**               |  **Title in Releases**  |\n|:-------------------------------------:|:-----------------------:|\n|       `enhancement`, `feature`        |       🚀 Features       |\n| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |\n|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |\n|              `breaking`               |   💥 Breaking Changes   |\n|            `documentation`            |    📝 Documentation     |\n|            `dependencies`             | ⬆️ Dependencies updates |\n\nYou can update it in [`release-drafter.yml`](https://github.com/Ce11an/spacy-cleaner/blob/main/.github/release-drafter.yml).\n\nGitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/Ce11an/spacy-cleaner)](https://github.com/Ce11an/spacy-cleaner/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/Ce11an/spacy-cleaner/blob/main/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{spacy-cleaner,\n  author = {spacy-cleaner},\n  title = {eEasily clean text with spaCy!},\n  year = {2022},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/Ce11an/spacy-cleaner}}\n}\n```\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'spacy-cleaner',
    'author_email': 'hallcellan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Ce11an/spacy-cleaner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
