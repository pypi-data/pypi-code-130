# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['testbench_tuna']

package_data = \
{'': ['*']}

install_requires = \
['fastapi>=0.78,<0.80', 'requests>=2.28.1,<3.0.0', 'uvicorn>=0.18.2,<0.19.0']

setup_kwargs = {
    'name': 'testbench-tuna',
    'version': '0.2.1',
    'description': 'Personal testbench for trying out stuff',
    'long_description': '# Testbench Tuna\n\n[![pypi package](https://badge.fury.io/py/testbench-tuna.svg)](https://pypi.python.org/pypi/testbench-tuna/)\n[![python](https://img.shields.io/pypi/pyversions/testbench-tuna.svg)](https://pypi.python.org/pypi/testbench-tuna)\n[![downloads](https://pepy.tech/badge/testbench-tuna)](https://pepy.tech/project/testbench-tuna)\n[![codecov](https://codecov.io/gh/trallnag/testbench-tuna/branch/trunk/graph/badge.svg?token=400YFJSVG7)](https://codecov.io/gh/trallnag/testbench-tuna)\n\nPersonal testbench where I try out things.\n\n- <https://github.com/googleapis/release-please>\n- <https://github.com/google-github-actions/release-please-action>\n',
    'author': 'Tim Schwenke',
    'author_email': 'tim.schwenke@trallnag.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/trallnag/testbench-tuna',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
