# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['papermill_origami']

package_data = \
{'': ['*']}

install_requires = \
['noteable-origami>=0.0.2,<0.0.3', 'papermill>=2.4.0,<3.0.0']

setup_kwargs = {
    'name': 'papermill-origami',
    'version': '0.0.2',
    'description': 'The noteable API interface',
    'long_description': '# papermill-origami\nA papermill engine for running Noteable notebooks\n\n<p align="center">\n<a href="https://github.com/noteable-io/papermill-origami/actions/workflows/ci.yaml">\n    <img src="https://github.com/noteable-io/papermill-origami/actions/workflows/ci.yaml/badge.svg" alt="CI" />\n</a>\n<img alt="PyPI - License" src="https://img.shields.io/pypi/l/papermill-origami" />\n<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/papermill-origami" />\n<img alt="PyPI" src="https://img.shields.io/pypi/v/papermill-origami">\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\n---------\n\n[Install](#installation) | [Getting Started](#getting-started) | [License](./LICENSE) | [Code of Conduct](./CODE_OF_CONDUCT.md) | [Contributing](./CONTRIBUTING.md)\n\n## Requirements\n\nPython 3.8+\n\n## Installation\n\n### Poetry\n\n```shell\npoetry add papermill-origami\n```\n\n\n### Pip\n```shell\npip install papermill-origami\n```\n\n## Getting Started\n\nGet your access token from https://app.noteable.world/api/token\n\n```python\nimport papermill as pm\nfrom papermill_origami import NoteableClient, ClientConfig\n\ndomain = \'app.noteable.world\'\ntoken = \'ey...\'\nfile_id = \'...\'\n\nasync with NoteableClient(token, config=ClientConfig(domain=domain)) as client:\n    file = await client.get_notebook(file_id)\n    pm.execute_notebook(\n        f\'noteable://{file_id}\',\n        None,\n        engine_name=\'noteable\', # exclude this kwarg to run the Notebook locally\n        # Noteable-specific kwargs\n        file=file,\n        client=client,\n    )\n```\n\n## Contributing\n\nSee [CONTRIBUTING.md](./CONTRIBUTING.md).\n\n-------\n\n<p align="center">Open sourced with ❤️ by <a href="https://noteable.io">Noteable</a> for the community.</p>\n\n<img href="https://pages.noteable.io/private-beta-access" src="https://assets.noteable.io/github/2022-07-29/noteable.png" alt="Boost Data Collaboration with Notebooks">\n',
    'author': 'Matt Seal',
    'author_email': 'matt@noteable.io',
    'maintainer': 'Matt Seal',
    'maintainer_email': 'matt@noteable.io',
    'url': 'https://github.com/noteable-io/papermill-origami',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
