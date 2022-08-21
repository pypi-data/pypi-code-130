# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['logseq_doctor']

package_data = \
{'': ['*']}

install_requires = \
['click', 'mistletoe']

entry_points = \
{'console_scripts': ['lsd = logseq_doctor.cli:main']}

setup_kwargs = {
    'name': 'logseq-doctor',
    'version': '0.1.1',
    'description': 'Logseq Doctor: heal your flat old Markdown files before importing them',
    'long_description': "========\nOverview\n========\n\n.. start-badges\n\n.. list-table::\n    :stub-columns: 1\n\n    * - docs\n      - |docs|\n    * - tests\n      - | |github-actions|\n        | |codecov|\n    * - package\n      - | |version| |wheel| |supported-versions| |supported-implementations|\n        | |commits-since|\n.. |docs| image:: https://readthedocs.org/projects/logseq-doctor/badge/?style=flat\n    :target: https://logseq-doctor.readthedocs.io/\n    :alt: Documentation Status\n\n.. |github-actions| image:: https://github.com/andreoliwa/logseq-doctor/actions/workflows/github-actions.yml/badge.svg\n    :alt: GitHub Actions Build Status\n    :target: https://github.com/andreoliwa/logseq-doctor/actions\n\n.. |codecov| image:: https://codecov.io/gh/andreoliwa/logseq-doctor/branch/master/graphs/badge.svg?branch=master\n    :alt: Coverage Status\n    :target: https://codecov.io/github/andreoliwa/logseq-doctor\n\n.. |version| image:: https://img.shields.io/pypi/v/logseq-doctor.svg\n    :alt: PyPI Package latest release\n    :target: https://pypi.org/project/logseq-doctor\n\n.. |wheel| image:: https://img.shields.io/pypi/wheel/logseq-doctor.svg\n    :alt: PyPI Wheel\n    :target: https://pypi.org/project/logseq-doctor\n\n.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/logseq-doctor.svg\n    :alt: Supported versions\n    :target: https://pypi.org/project/logseq-doctor\n\n.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/logseq-doctor.svg\n    :alt: Supported implementations\n    :target: https://pypi.org/project/logseq-doctor\n\n.. |commits-since| image:: https://img.shields.io/github/commits-since/andreoliwa/logseq-doctor/v0.1.1.svg\n    :alt: Commits since latest release\n    :target: https://github.com/andreoliwa/logseq-doctor/compare/v0.1.1...master\n\n\n\n.. end-badges\n\nLogseq Doctor: heal your flat old Markdown files before importing them.\n\n**Note:** *this project is still alpha, so it's a bit rough on the edges (documentation and feature-wise).*\n\nInstallation\n============\n\nThe recommended way is to install ``logseq-doctor`` globally with `pipx <https://github.com/pypa/pipx>`_::\n\n    pipx install logseq-doctor\n\nYou can also install the development version with::\n\n    pipx install git+https://github.com/andreoliwa/logseq-doctor\n\nYou will then have the ``lsd`` command available globally in your system.\n\nQuick start\n===========\n\nUse ``--help`` to check the current commands and options.\n\nExample output::\n\n    $ lsd --help\n    Usage: lsd [OPTIONS] COMMAND [ARGS]...\n\n      Logseq Doctor: heal your flat old Markdown files before importing them.\n\n    Options:\n      --help  Show this message and exit.\n\n    Commands:\n      outline  Convert flat Markdown to outline.\n\n    $ lsd outline --help\n    Usage: lsd outline [OPTIONS] FILE\n\n      Convert flat Markdown to outline.\n\n    Options:\n      --help  Show this message and exit.\n\nDocumentation\n=============\n\n\nhttps://logseq-doctor.readthedocs.io/\n\n\nDevelopment\n===========\n\nTo run all the tests run::\n\n    tox\n\nNote, to combine the coverage data from all the tox environments run:\n\n.. list-table::\n    :widths: 10 90\n    :stub-columns: 1\n\n    - - Windows\n      - ::\n\n            set PYTEST_ADDOPTS=--cov-append\n            tox\n\n    - - Other\n      - ::\n\n            PYTEST_ADDOPTS=--cov-append tox\n",
    'author': 'W. Augusto Andreoli',
    'author_email': 'andreoliwa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/andreoliwa/logseq-doctor',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
