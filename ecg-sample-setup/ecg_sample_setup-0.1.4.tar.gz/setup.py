# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ecg_sample_setup']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.1.14,<2.0.0']

setup_kwargs = {
    'name': 'ecg-sample-setup',
    'version': '0.1.4',
    'description': '',
    'long_description': '\n# ecgai-sample-setup\n\n > Easily extend JSON to encode and decode arbitrary Python objects.\n\n[![PyPI version][pypi-image]][pypi-url]\n[![Build status][build-image]][build-url]\n[![Code coverage][coverage-image]][coverage-url]\n\n[//]: # ([![GitHub stars][stars-image]][stars-url])\n\n[//]: # ([![Support Python versions][versions-image]][versions-url])\n...\n\n\nfrom article at https://mathspp.com/blog/how-to-create-a-python-package-in-2022\n\njust a test package to help me setup next time\n\n<!-- Badges: -->\n\n[pypi-image]: https://img.shields.io/pypi/v/ecg_sample_setup\n[pypi-url]: https://pypi.org/project/ecg_sample_setup/\n[build-image]: https://github.com/Ecg-Ai-com/ecgai-sample-setup/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/Ecg-Ai-com/ecg-sample-setup/actions/workflows/build.yaml\n[coverage-image]: https://codecov.io/gh/Ecg-Ai-com/ecg-sample-setup/branch/main/graph/badge.svg\n[coverage-url]: https://codecov.io/gh/Ecg-Ai-com/ecg-sample-setup/\n[stars-image]: https://img.shields.io/github/stars/Ecg-Ai-com/ecg-sample-setup/\n[stars-url]: https://github.com/Ecg-Ai-com/ecg-sample-setup\n[versions-image]: https://img.shields.io/pypi/pyversions/ecg-sample-setup/\n[versions-url]: https://pypi.org/project/ecg-sample-setup/\n',
    'author': 'RobC',
    'author_email': 'rob.clapham@gmail.com',
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
