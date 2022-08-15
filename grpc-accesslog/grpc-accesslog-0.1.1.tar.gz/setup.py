# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['grpc_accesslog']

package_data = \
{'': ['*']}

install_requires = \
['grpc-interceptor>=0.13.0', 'grpc-stubs>=1.24.5']

entry_points = \
{'console_scripts': ['grpc-accesslog = grpc_accesslog.__main__:main']}

setup_kwargs = {
    'name': 'grpc-accesslog',
    'version': '0.1.1',
    'description': 'gRPC Access Log',
    'long_description': "gRPC Access Log\n===============\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/grpc-accesslog.svg\n   :target: https://pypi.org/project/grpc-accesslog/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/grpc-accesslog.svg\n   :target: https://pypi.org/project/grpc-accesslog/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/grpc-accesslog\n   :target: https://pypi.org/project/grpc-accesslog\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/grpc-accesslog\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/grpc-accesslog/latest.svg?label=Read%20the%20Docs\n   :target: https://grpc-accesslog.readthedocs.io/\n   :alt: Read the documentation at https://grpc-accesslog.readthedocs.io/\n.. |Tests| image:: https://github.com/villainy/grpc-accesslog/workflows/Tests/badge.svg\n   :target: https://github.com/villainy/grpc-accesslog/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/villainy/grpc-accesslog/branch/main/graph/badge.svg\n   :target: https://app.codecov.io/gh/villainy/grpc-accesslog\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* Write stdout logs for every RPC request\n* Log messages built with customizable callback handlers\n\n\nRequirements\n------------\n\n* Python 3.7+\n* grpc-interceptors 0.13+\n\n\nInstallation\n------------\n\nYou can install *gRPC Access Log* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install grpc-accesslog\n\n\nUsage\n-----\n\nPlease see the `Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*gRPC Access Log* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/villainy/grpc-accesslog/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: https://grpc-accesslog.readthedocs.io/en/latest/contributing.html\n.. _Usage: https://grpc-accesslog.readthedocs.io/en/latest/usage.html\n",
    'author': 'Michael Morgan',
    'author_email': 'git@morgan83.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/villainy/grpc-accesslog',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
