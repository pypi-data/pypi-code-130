# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['azpkg37']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.3,<4.0.0']

setup_kwargs = {
    'name': 'azpkg37',
    'version': '0.1.0',
    'description': 'AZ Testing Package',
    'long_description': '# azpkg\n\nAZ Testing Package\n\n## Installation\n\n```bash\n$ pip install azpkg\n```\n\n## Usage\n\n- TODO\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`azpkg` was created by AraonZ. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`azpkg` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'AraonZ',
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
