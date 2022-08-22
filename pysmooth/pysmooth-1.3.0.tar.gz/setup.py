# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pysmooth']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22,<2.0']

setup_kwargs = {
    'name': 'pysmooth',
    'version': '1.3.0',
    'description': "Pysmooth: a Python implementation of R's stats::smooth Tukey's (running median) smoother",
    'long_description': 'Pysmooth\n==========\n\nA Python implementation of R\'s stats::smooth() Tukey\'s (running median) smoother\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n|Repobeats analytics image|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/pysmooth.svg\n   :target: https://pypi.org/project/pysmooth/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/pysmooth.svg\n   :target: https://pypi.org/project/pysmooth/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/pysmooth\n   :target: https://pypi.org/project/pysmooth\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/pysmooth\n   :target: https://opensource.org/licenses/GPL-3.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/pysmooth/latest.svg?label=Read%20the%20Docs\n   :target: https://pysmooth.readthedocs.io/\n   :alt: Read the documentation at https://pysmooth.readthedocs.io/\n.. |Tests| image:: https://github.com/milescsmith/pysmooth/workflows/Tests/badge.svg\n   :target: https://github.com/milescsmith/pysmooth/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/milescsmith/pysmooth/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/milescsmith/pysmooth\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n.. |Repobeats analytics image| image:: https://repobeats.axiom.co/api/embed/6870249c18b93b2fcc0d967ec9f7308d74ca42cc.svg\n   :target: https://repobeats.axiom.co\n   :alt: Repobeats analytics image\n\nFeatures\n--------\n\n* TODO\n  - Replace C/R-style coding with more Pythonic methods\n\n\nRequirements\n------------\n\n* Python 3.8, 3.9, or 3.10\n* Numpy 1.20\n\n\nInstallation\n------------\n\nYou can install *pysmooth* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install pysmooth\n\n\nUsage\n-----\n\nPysmooth is intended to be used within another module.\n\n.. code:: console\n\n   from pysmooth import smooth\n\n   smooth(x=arr, kind="3RS3R", twiceit=False, endrule="Tukey")\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `GPL 3.0 license`_,\n*Pysmooth* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _GPL 3.0 license: https://opensource.org/licenses/GPL-3.0\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/milescsmith/pysmooth/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://pysmooth.readthedocs.io/en/latest/usage.html\n',
    'author': 'Miles Smith',
    'author_email': 'mileschristiansmith@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/milescsmith/pysmooth',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
