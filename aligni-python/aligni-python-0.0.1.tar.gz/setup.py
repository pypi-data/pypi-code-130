# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['aligni']

package_data = \
{'': ['*']}

install_requires = \
['ratelimit>=2.2', 'requests>=2.25']

setup_kwargs = {
    'name': 'aligni-python',
    'version': '0.0.1',
    'description': 'Python library for interfacing to the Aligni (PLM/MRP) API',
    'long_description': '# Aligni Python\n\n[![PyPI](https://img.shields.io/pypi/v/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)\n[![PyPI - License](https://img.shields.io/pypi/l/aligni-python?style=flat-square)](https://pypi.python.org/pypi/aligni-python/)\n\n---\n\n**Source Code**: [https://github.com/mnorman-dev/aligni-python](https://github.com/mnorman-dev/aligni-python)\n\n**PyPI**: [https://pypi.org/project/aligni-python/](https://pypi.org/project/aligni-python/)\n\n---\n\nPython library for interfacing to the Aligni (PLM/MRP) API v2\n\nFull documentation of the underlying API is available at: [https://api.aligni.com/v2/index.html](https://api.aligni.com/v2/index.html)\n\n**WARNING** This code should be considered beta level at best.  A good understanding of the underlying api is required to understand the data available for each datatype.\n\n## Usage\n\nBelow is a simple example of how to use this interface to query the parts in a library.  This example uses the demo Aligni site at [https://demo.aligni.com/](https://demo.aligni.com/).\n```python\nimport aligni.api\n\nif __name__ == "__main__":\n  sitename = "demo"  # Replace with sitename of Aligni account\n  apikey = "oid3vLgynoy_Yl1gZkrgkLEq3J"  # Replace with API Key created from Aligni account\n\n  aligni_api = aligni.api.API(sitename, apikey)\n  aligni_parts = aligni_api.parts.get_list()\n  aligni_total_part_count = len(aligni_parts)\n  print("Aligni Part Count =", aligni_total_part_count)\n```\n\nRefer to tests to see further examples.\n\n## Installation\n\n```sh\npip install aligni-python\n```\n\n## Development\n\n- Clone this repository\n- Requirements:\n  - [Poetry](https://python-poetry.org/)\n  - Python 3.7+\n- Create a virtual environment and install the dependencies\n\n```sh\npoetry install\n```\n\n- Activate the virtual environment\n\n```sh\npoetry shell\n```\n\n### Testing\n\n```sh\npytest\n```\n\n### Pre-commit\n\nPre-commit hooks run all the auto-formatters (e.g. `black`, `isort`), linters (e.g. `mypy`, `flake8`), and other quality\nchecks to make sure the changeset is in good shape before a commit/push happens.\n\nYou can install the hooks with (runs for each commit):\n\n```sh\npre-commit install\n```\n\nOr if you want them to run only for each push:\n\n```sh\npre-commit install -t pre-push\n```\n\nOr if you want e.g. want to run all checks manually for all files:\n\n```sh\npre-commit run --all-files\n```\n',
    'author': 'Mark Norman',
    'author_email': 'mpnorman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mnorman-dev.github.io/aligni-python',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
