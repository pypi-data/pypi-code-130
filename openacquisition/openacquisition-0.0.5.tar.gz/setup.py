# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openacquisition',
 'openacquisition.algorithms',
 'openacquisition.chemistry',
 'openacquisition.filters',
 'openacquisition.instrumentation',
 'openacquisition.mathematics',
 'openacquisition.methods',
 'openacquisition.simulation',
 'openacquisition.triggers']

package_data = \
{'': ['*']}

install_requires = \
['lazy>=1.4,<2.0', 'mistune>=2.0.4,<3.0.0', 'pyopenms>=2.7.0,<3.0.0']

setup_kwargs = {
    'name': 'openacquisition',
    'version': '0.0.5',
    'description': 'A package for creating data acquisition methods for mass spectrometers',
    'long_description': '# OpenAcquisition\n[![License: MIT](https://img.shields.io/github/license/DennisGoldfarb/OpenAcquisition)](https://opensource.org/licenses/MIT)\n[![Documentation Status](https://readthedocs.org/projects/openacquisition/badge/?version=main)](https://openacquisition.readthedocs.io/en/main/?badge=main)\n![Build](https://github.com/DennisGoldfarb/OpenAcquisition/actions/workflows/ci-cd.yml/badge.svg)\n[![codecov](https://codecov.io/gh/DennisGoldfarb/OpenAcquisition/branch/main/graph/badge.svg?token=CIMEPT9GCZ)](https://codecov.io/gh/DennisGoldfarb/OpenAcquisition)\n[![Version](https://img.shields.io/pypi/v/openacquisition)](https://pypi.org/project/openacquisition/)\n\n\nPython library to create data acquisition algorithms for mass spectrometers\n\n## Requirements\n\n## Installation\n\n```bash\n$ pip install openacquisition\n```\n\n## Usage\n\n## Contributing\nInterested in contributing? Check out the contributing guidelines. \nPlease note that this project is released with a Code of Conduct. \nBy contributing to this project, you agree to abide by its terms.\n\n## License\n`OpenAcquisition` was created by the [Goldfarb Lab](https://sites.wustl.edu/goldfarblab) at Washington University School of Medicine in St. Louis. It is licensed under the terms of the MIT license.\n',
    'author': 'Dennis Goldfarb',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
