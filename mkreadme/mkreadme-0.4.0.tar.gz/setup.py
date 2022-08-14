# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mkreadme']

package_data = \
{'': ['*'], 'mkreadme': ['static/*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.1.3,<9.0.0',
 'inquirer>=2.10.0,<3.0.0',
 'pydantic>=1.9.2,<2.0.0']

entry_points = \
{'console_scripts': ['mkreadme = mkreadme.__main__:main']}

setup_kwargs = {
    'name': 'mkreadme',
    'version': '0.4.0',
    'description': 'A cli tool to interactively generate a README file',
    'long_description': '# mkreadme\n\n[![PyPI version](https://badge.fury.io/py/mkreadme.svg)](https://badge.fury.io/py/mkreadme)\n[![Python version](https://img.shields.io/badge/python-≥3.8-blue.svg)](https://pypi.org/project/kedro/)\n[![Release Pipeline](https://github.com/AnH0ang/mkreadme/actions/workflows/release.yml/badge.svg)](https://github.com/AnH0ang/mkreadme/actions/workflows/release.yml)\n[![Code Quality](https://github.com/AnH0ang/mkreadme/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AnH0ang/mkreadme/actions/workflows/code_quality.yml)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/AnH0ang/nbenumerate/blob/master/LICENCE)\n![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)\n\n## 📝 Description\n\n`mkreadme` is a cli tool for interactive creation of a `README.md` file. It was inspired by [readme.so](https://readme.so/). You can choose from different `README` sections, which are then merged into a complete document.\n\n## ⚙️ Installation\n\nInstall `mkreadme` with `pip`\n\n```bash\n  pip install mkreadme\n```\n\n## 💡 Usage Examples\n\nTo interactively create a README file with `mkreadme`, run\n\n```console\nmkreadme --filename README.md\n```\n\n## 🖼️ Screenshots\n\n![App Screenshot](static/Screenshot.png)\n',
    'author': 'An Hoang',
    'author_email': 'anhoang31415@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/mkreadme/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
