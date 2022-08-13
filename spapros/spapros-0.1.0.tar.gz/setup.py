# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spapros',
 'spapros.cli',
 'spapros.design',
 'spapros.design.src',
 'spapros.evaluation',
 'spapros.plotting',
 'spapros.selection',
 'spapros.util']

package_data = \
{'': ['*'], 'spapros.design': ['data/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'Pillow==9.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'UpSetPlot>=0.6.0,<0.7.0',
 'bandit==1.7.2',
 'click>=8.0.1,<9.0.0',
 'jupyter-sphinx>=0.3.2,<0.4.0',
 'leidenalg>=0.8.7,<0.9.0',
 'matplotlib>=3.4.1,<4.0.0',
 'nox-poetry>=0.9.0,<0.10.0',
 'nox>=2022.1.7,<2023.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pandoc>=2.1,<3.0',
 'pypi-latest>=0.1.0,<0.2.0',
 'questionary>=1.10.0,<2.0.0',
 'rich>=10.1.0',
 'ruamel.yaml>=0.17.10,<0.18.0',
 'scanpy>=1.8.1,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'venndata>=0.1.0,<0.2.0',
 'xgboost>=1.6.1,<2.0.0']

entry_points = \
{'console_scripts': ['spapros = spapros.__main__:main']}

setup_kwargs = {
    'name': 'spapros',
    'version': '0.1.0',
    'description': 'Probe set selection for targeted spatial transcriptomics.',
    'long_description': 'spapros\n==========\n\n|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/spapros.svg\n   :target: https://pypi.org/project/spapros/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/spapros\n   :target: https://pypi.org/project/spapros\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/theislab/spapros\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/spapros/latest.svg?label=Read%20the%20Docs\n   :target: https://spapros.readthedocs.io/\n   :alt: Read the documentation at https://spapros.readthedocs.io/\n.. |Build| image:: https://github.com/theislab/spapros/workflows/Build%20spapros%20Package/badge.svg\n   :target: https://github.com/theislab/spapros/workflows/Build%20spapros%20Package/badge.svg\n   :alt: Build package Status\n.. |Tests| image:: https://github.com/theislab/spapros/actions/workflows/run_tests.yml/badge.svg\n   :target: https://github.com/theislab/spapros/actions/workflows/run_tests.yml/badge.svg\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/theislab/spapros/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/theislab/spapros\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n|logo|\n\nFeatures\n--------\n\n* Select probe sets for targeted spatial transcriptomics\n* Evaluate probe sets with an extensive pipeline\n\n\nInstallation\n------------\n\nYou can install *spapros* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install spapros\n\n\nUsage\n-----\n\nVisit our `documentation`_ for installation, tutorials, examples and more.\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. |logo| image:: https://user-images.githubusercontent.com/21954664/111175015-409d9080-85a8-11eb-9055-f7452aed98b2.png\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT: http://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://spapros.readthedocs.io/en/latest/usage.html\n.. _documentation: https://spapros.readthedocs.io/en/latest/\n',
    'author': 'Lukas Heumos',
    'author_email': 'lukas.heumos@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/spapros',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
