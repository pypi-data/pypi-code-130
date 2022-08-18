# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clidantic']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.0,<9.0.0', 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'clidantic',
    'version': '0.1.0',
    'description': 'Typed Command Line Interfaces powered by Click and Pydantic',
    'long_description': '# clidantic\nTyped Command Line Interfaces powered by Click and Pydantic.\n\n> :warning: **Library in early alpha stage**\n\n[![test passing](https://img.shields.io/github/workflow/status/edornd/clidantic/Test)](https://github.com/edornd/clidantic)\n[![coverage](https://img.shields.io/codecov/c/github/edornd/clidantic)](https://codecov.io/gh/edornd/clidantic)\n[![pypi version](https://img.shields.io/pypi/v/clidantic)](https://pypi.org/project/clidantic/)\n[![python versions](https://img.shields.io/pypi/pyversions/clidantic)](https://github.com/edornd/clidantic)\n\n---\n## Documentation\n\nThe first draft of documentation is available here: [https://edornd.github.io/clidantic/](https://edornd.github.io/clidantic/)\n\n## Installing\nThe safest path is to install the latest release using pip:\n```\npip install clidantic\n```\nOptionally, you can install the latest updates through GitHub:\n```\npip install git+https://github.com/edornd/clidantic.git\n```\nor, if that doesn\'t work, with multiple steps (this last step might require [poetry](https://python-poetry.org/)):\n```\ngit clone https://github.com/edornd/clidantic.git\ncd clidantic\npip install .\n```\n\n## Quickstart\nHere\'s a quick example to get you started:\n```python\nfrom typing import Optional\nfrom pydantic import BaseModel\n\nfrom clidantic import Parser\n\n\nclass Arguments(BaseModel):\n    field_a: str\n    field_b: int\n    field_c: Optional[bool] = False\n\n\ncli = Parser()\n\n\n@cli.command()\ndef main(args: Arguments):\n    print(args)\n\n\nif __name__ == "__main__":\n    cli()\n```\n\n\n## Contributing\nWe are not quite there yet!\n',
    'author': 'Edoardo Arnaudo',
    'author_email': 'edoardo.arn@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/edornd/clidantic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
