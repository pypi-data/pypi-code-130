# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cft_analysis',
 'cft_analysis.datasets',
 'cft_analysis.feature_extraction',
 'cft_analysis.utils']

package_data = \
{'': ['*']}

install_requires = \
['biopsykit[jupyter]>=0.6,<0.7', 'tpcp>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'cft-analysis',
    'version': '1.1.0',
    'description': 'Package for the analysis of Cold Face Test Data.',
    'long_description': '# cft-analysis\n\n[![PyPI](https://img.shields.io/pypi/v/cft-analysis)](https://pypi.org/project/cft-analysis/)\n![GitHub](https://img.shields.io/github/license/mad-lab-fau/cft-analysis)\n[![Lint](https://github.com/mad-lab-fau/cft-analysis/actions/workflows/lint.yml/badge.svg)](https://github.com/mad-lab-fau/cft-analysis/actions/workflows/lint.yml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mad-lab-fau/cft-analysis)\n\nPython package for the analysis of data collected during the Cold Face Test (CFT) study.\n\n## Description\n\nThis package contains various helper functions to work with the dataset (including [`tpcp`](https://github.com/mad-lab-fau/tpcp) `Dataset` representations) and to process data. Additionally, it contains different analysis experiments performed with the dataset.\n\n## Repository Structure\nThe repository is structured as follows:\n\n```bash\n├── cft_analysis/                                   # cft-analysis Python package\n└── experiments/                                    # Folder with conducted analysis experiments; each experiment has its own subfolder\n    └── 2022_scientific_reports/                    # Analysis for the 2022 Scientific Reports Paper (see below)\n        ├── data/                                   # Processed data and extracted parameters\n        ├── notebooks/                              # Notebooks for data processing, analysis and plotting\n        │   ├── data_processing/            \n        │   │   ├── ECG_Processing_Feature_Computation.ipynb    # Processing and feature extraction from ECG data\n        │   │   ├── Questionnaire_Processing.ipynb              # Processing of questionnaire data\n        │   │   └── Saliva_Processing.ipynb                     # Processing of saliva data\n        │   ├── analysis/                   \n        │   │   ├── Subject_Exclusion.ipynb         # Checks whether (and which) subjects need to be excluded from further analysis\n        │   │   ├── Demographics.ipynb              # Analysis of general information of study population: Age, Gender, BMI, ...\n        │   │   ├── ECG_Analysis.ipynb              # Descriptive and statistical analysis of ECG data\n        │   │   ├── Questionnaire_Analysis.ipynb    # Descriptive and statistical analysis of questionnaire data\n        │   │   └── Saliva_Analysis.ipynb           # Descriptive and statistical analysis of saliva data\n        │   └── plotting/\n        ├── results/                                # Plots and statistical results exported by the notebooks in the "analysis" and "plotting" folders\n        └── config.json                             # \n\n```\n\n## Installation\nIf you want to use this package to reproduce the analysis results then clone the repository and install the \npackage via [poetry](https://python-poetry.org):\n```bash\ngit clone git@github.com:mad-lab-fau/cft-analysis.git\ncd cft-analysis\npoetry install # alternative: pip install .\n```\nThis creates a new python venv in the `cft-analysis/.venv` folder. Next, register a new IPython kernel for the venv:\n```bash\ncd cft-analysis\npoetry run poe register_ipykernel\n```\n\nFinally, go to the `experiments` folder and run the Jupyter Notebooks. \n\n## Experiments\nCurrently, this repository contains the following experiments:\n\n### 2022 – Scientific Reports\nAnalysis of the [CFT Dataset](https://osf.io/8fb6n/) for the paper "Vagus Activation by Cold Face Test Reduces Acute Psychosocial Stress Responses", submitted to *Scientific Reports* [TODO: update when published].\n\n#### Usage\nIn order to run the code, first download the CFT Dataset, e.g. from [OSF](https://osf.io/8fb6n/). Then, create a file named `config.json` in the folder `/experiments/2022_scientific_reports` with the following content:\n```json\n{\n    "base_path": "<path-to-dataset>"\n}\n```\nThis config file is parsed by all notebooks to extract the path to the dataset.   \n**NOTE**: This file is ignored by git because the path to the dataset depends on the local configuration!\n\nThe files in the `data` folder are created by running the notebooks in the `data_processing` folder. The files in the `result` folder are created by running the notebooks in the `analysis` and the `plotting` folders.\n\n\n\n\n',
    'author': 'Robert Richer',
    'author_email': 'robert.richer@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/cft-analysis',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
