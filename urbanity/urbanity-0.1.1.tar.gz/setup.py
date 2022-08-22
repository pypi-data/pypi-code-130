# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['urbanity']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'urbanity',
    'version': '0.1.1',
    'description': 'Urbanity is a python package to model and understand urban complexity.',
    'long_description': '# urbanity\n\nUrbanity is a python package to model and understand urban complexity. This package is currently under development.\n\n## Installation\n\n```Terminal\n$ pip install urbanity\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`urbanity` was created by winstonyym. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`urbanity` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'winstonyym',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
