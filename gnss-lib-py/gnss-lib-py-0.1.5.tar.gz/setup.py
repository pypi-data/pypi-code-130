# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gnss_lib_py',
 'gnss_lib_py.algorithms',
 'gnss_lib_py.parsers',
 'gnss_lib_py.utils']

package_data = \
{'': ['*']}

install_requires = \
['DateTime>=4.3,<5.0',
 'georinex>=1.15.0,<2.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.3.0,<2.0.0',
 'plotly>=5.8.0,<6.0.0',
 'pylint>=2.11.1,<3.0.0',
 'pynmea2>=1.18.0,<2.0.0',
 'pytest-cov>=3.0.0,<4.0.0',
 'pytest-lazy-fixture>=0.6.3,<0.7.0',
 'pytest>=6.2.5,<7.0.0',
 'reindent>=3.5.1,<4.0.0',
 'scipy>=1.7.3,<2.0.0',
 'unlzw3>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'gnss-lib-py',
    'version': '0.1.5',
    'description': 'Modular Python tool for parsing, analyzing, and visualizing Global Navigation Satellite Systems (GNSS) data',
    'long_description': '[![build](https://github.com/Stanford-NavLab/gnss_lib_py/actions/workflows/python-app.yml/badge.svg)](https://github.com/Stanford-NavLab/gnss_lib_py/actions/workflows/python-app.yml)\n[![codecov](https://codecov.io/gh/Stanford-NavLab/gnss_lib_py/branch/main/graph/badge.svg?token=1FBGEWRFM6)](https://codecov.io/gh/Stanford-NavLab/gnss_lib_py)\n[![Documentation Status](https://readthedocs.org/projects/gnss_lib_py/badge/?version=latest)](https://gnss_lib_py.readthedocs.io/en/latest/?badge=latest)\n\ngnss_lib_py\n===========\n\n`gnss_lib_py` is a modular Python tool for parsing, analyzing, and\nvisualizing Global Navigation Satellite Systems (GNSS) data.\nIt also provides an intuitive and modular framework allowing users to\nquickly prototype, implement, and visualize GNSS algorithms.\n`gnss_lib_py` is modular in the sense that multiple types of\nalgorithms can be easily exchanged for each other and extendable in\nfacilitating user-specific extensions of existing implementations.\n\n<img src="https://raw.githubusercontent.com/Stanford-NavLab/gnss_lib_py/main/docs/source/img/skyplot.png" alt="satellite skyplot" width="600"/>\n\n`gnss_lib_py` contains parsers for common file types used for\nstoring GNSS measurements, benchmark algorithms for processing\nmeasurements into state estimates and visualization tools for measurements\nand state estimates.\nThe modularity of `gnss_lib_py` is made possibly by the unifying\n`NavData` class, which contains methods to add, remove and modify\nnumeric and string data consistently.\nWe provide standard row names for `NavData` elements on the\n[reference page](https://gnss-lib-py.readthedocs.io/en/latest/reference/reference.html).\nThese names ensure cross compatability between different datasets and\nalgorithms.\n\nDocumentation\n-------------\nFull documentation is available on our [readthedocs website](https://gnss-lib-py.readthedocs.io/en/latest/index.html).\n\n\nCode Organization\n-----------------\n\n`gnss_lib_py` is organized as:\n\n```bash\n\n   ├── data/                          # Location for data files\n      └── unit_test/                  # Data files for unit testing\n   ├── dev/                           # Code users do not wish to commit\n   ├── docs/                          # Documentation files\n   ├── gnss_lib_py/                   # gnss_lib_py source files\n        ├── algorithms/               # Navigation algorithms\n        ├── parsers/                  # Data parsers\n        ├── utils/                    # GNSS and common utilities\n        └── __init__.py\n   ├── notebooks/                     # Interactive Jupyter notebooks\n        ├── tutorials/                # Notebooks with tutorial code\n   ├── results/                       # Location for result images/files\n   ├── tests/                         # Tests for source files\n      ├── algorithms/                 # Tests for files in algorithms\n      ├── parsers/                    # Tests for files in parsers\n      ├── utils/                      # Tests for files in utils\n      └── test_gnss_lib_py.py         # High level checks for repository\n   ├── CONTRIBUTORS.md                # List of contributors\n   ├── build_docs.sh                  # Bash script to build docs\n   ├── poetry.lock                    # Poetry specific Lock file\n   ├── pyproject.toml                 # List of package dependencies\n   ├── requirements.txt               # List of packages for pip install\n   └── setup.py                       # Setup file\n```\nIn the directory organization above:\n\n  * The `algorithms` directory contains localization algorithms that\n    work by passing in a `NavData` class. Currently, the following\n    algorithms are implemented in the `algorithms`:\n\n      * Weighted Least Squares\n      * Calculating pseudorange residuals\n  * The data parsers in the `parsers` directory allow for loading\n    GNSS data into `gnss_lib_py`\'s unifying `NavData` class.\n    Currently, the following datasets and types are supported:\n\n      * [2021 Google Android Derived Dataset](https://www.kaggle.com/c/google-smartphone-decimeter-challenge)\n\n  * The `utils` directory contains utilities used to handle\n    GNSS measurements, time conversions, visualizations, satellite\n    simulation, file operations, etc.\n  * Currently, the following data visualization tools are available in the\n    `utils` directory:\n\n        * Skyplot: showing the movement of GNSS satellites during the\n          elapsed time of the provided `NavData` class.\n        * Metric plotting: allows you to plot a specific array of data\n          from the `NavData` class\n        * Metric plotting by constellation: allows you to plot a specific\n          array of data but broken up by individual constellations and\n          signal types.\n        * Residual plotting: specifically optimized for plotting residuals.\n\n\nInstallation\n------------\nFor directions on how to install the `gnss_lib_py` project, please\nsee the [install instructions](https://gnss-lib-py.readthedocs.io/en/latest/install.html).\n\nTutorials\n---------\nWe have a range of tutorials on how to easily use this project. They can\nall be found in the [tutorials section](https://gnss-lib-py.readthedocs.io/en/latest/tutorials/tutorials.html).\n\nReference\n---------\nReferences on the package contents, explanation of the benefits of our\ncustom NavData class, and function-level documentation can all be\nfound in the [reference section](https://gnss-lib-py.readthedocs.io/en/latest/reference/reference.html).\n\nContributing\n------------\nIf you have a bug report or would like to contribute to our repository,\nplease follow the guide on the [contributing page](https://gnss-lib-py.readthedocs.io/en/latest/contributing/contributing.html).\n\nTroubleshooting\n---------------\nAnswers to common questions can be found in the [troubleshooting section](https://gnss-lib-py.readthedocs.io/en/latest/troubleshooting.html).\n\nAttribution\n-----------\nThis project is a product of the [Stanford NAV Lab](https://navlab.stanford.edu/)\nand currently maintained by Ashwin Kanhere and Derek Knowles. If using\nthis project in your own work please cite the following:\n\n```\n\n   @inproceedings{knowlesmodular2022,\n      title = {A Modular and Extendable GNSS Python Library},\n      author={Knowles, Derek and Kanhere, Ashwin V and Bhamidipati, Sriramya and Gao, Grace},\n      booktitle={Proceedings of the 35th International Technical Meeting of the Satellite Division of The Institute of Navigation (ION GNSS+ 2022)},\n      institution = {Stanford University},\n      year = {2022 [Online]},\n      url = {https://github.com/Stanford-NavLab/gnss_lib_py},\n   }\n```\n\nAdditionally, we would like to thank [all contributors](https://github.com/Stanford-NavLab/gnss_lib_py/blob/main/CONTRIBUTORS.md) to this project.\n',
    'author': 'Derek Knowles',
    'author_email': 'dcknowles@stanford.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Stanford-NavLab/gnss_lib_py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
