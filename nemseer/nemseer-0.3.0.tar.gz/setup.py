# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nemseer', 'nemseer.downloader_helpers']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21,<22',
 'beautifulsoup4>=4,<5',
 'dask>=2022.7.1,<2023.0.0',
 'netCDF4>=1.6.0,<2.0.0',
 'numpy>=1.23.0,<2.0.0',
 'packaging>=21.3,<22.0',
 'pandas>=1.2,<2.0',
 'psutil>=5.9.1,<6.0.0',
 'pyarrow>=8.0.0,<9.0.0',
 'requests>=2,<3',
 'tqdm>=4.64.0,<5.0.0',
 'xarray>=2022,<2023']

setup_kwargs = {
    'name': 'nemseer',
    'version': '0.3.0',
    'description': 'A package for downloading and handling forecasts for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO).',
    'long_description': "# nemseer\n\n[![PyPI version](https://badge.fury.io/py/nemseer.svg)](https://badge.fury.io/py/nemseer)\n[![Continuous Integration and Deployment](https://github.com/UNSW-CEEM/NEMSEER/actions/workflows/cicd.yml/badge.svg)](https://github.com/UNSW-CEEM/NEMSEER/actions/workflows/cicd.yml)\n[![Documentation Status](https://readthedocs.org/projects/nemseer/badge/?version=latest)](https://nemseer.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/UNSW-CEEM/NEMSEER/branch/master/graph/badge.svg?token=BO69YSQIGI)](https://codecov.io/gh/UNSW-CEEM/NEMSEER)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nA package for downloading and handling forecasts for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO).\n\n## Work in Progress\n\nThis package is a work in progress. For a high-level overview of development, check out the [roadmap](./ROADMAP.md).\n\n## Installation\n\n```bash\npip install nemseer\n```\n\n## Overview\n\n`nemseer` allows you to access AEMO [pre-dispatch](https://aemo.com.au/en/energy-systems/electricity/national-electricity-market-nem/data-nem/market-management-system-mms-data/pre-dispatch) and [Projected Assessment of System Adequacy (PASA)](https://wa.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/nem-forecasting-and-planning/forecasting-and-reliability/projected-assessment-of-system-adequacy) forecast data.\n\n![forecast_overview](docs/source/_static/forecast_timeframes.png)\n\n<sub><sup>Source: [Reserve services in the National Electricity Market, AEMC, 2021](https://www.aemc.gov.au/sites/default/files/2020-12/AEMC_Reserve%20services%20in%20the%20NEM%20directions%20paper_05.01.2021.pdf)</sup></sub>\n\nSpecifically, `nemseer` enables you to download:\n\n1. 5-minute pre-dispatch (`P5MIN`: [Tables and Descriptions](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_222.htm#1))\n2. [Pre-dispatch](https://www.aemo.com.au/-/media/files/electricity/nem/security_and_reliability/power_system_ops/procedures/so_op_3704-predispatch.pdf?la=en) (`PREDISPATCH`: [Tables and Descriptions](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_260.htm#1))\n3. Pre-dispatch Projected Assessment of System Adequacy (`PDPASA`: [Tables and Descriptions](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_467.htm#1))\n4. [Short Term Projected Assessment of System Adequacy](https://wa.aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/pasa/stpasa-process-description.pdf) (`STPASA`: [Tables and Descriptions](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_335.htm#1))\n5. [Medium Term Projected Assessment of System Adequacy](https://wa.aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/pasa/mt-pasa-process-description-v62.pdf?la=en) (`MTPASA`: [Tables and Descriptions](https://nemweb.com.au/Reports/Current/MMSDataModelReport/Electricity/MMS%20Data%20Model%20Report_files/MMS_210.htm#1))\n\nAnother helpful reference for PASA information is AEMO's [Reliability Standard Implementation Guidelines](https://www.aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/rsig/reliability-standard-implementation-guidelines.pdf?la=en).\n\n### ST PASA Replacement Project\n\nNote that the methodologies for PD PASA and ST PASA are being reviewed. In particular, the ST PASA Replacement project will combine PD PASA and ST PASA into ST PASA. For more detail, refer to the [final determination of the rule change](https://www.aemc.gov.au/sites/default/files/2022-05/ERC0332%20-%20Updating%20Short%20Term%20PASA%20-%20Final%20determination.pdf) and the [AEMO ST PASA Replacement Project home page](https://aemo.com.au/en/initiatives/trials-and-initiatives/st-pasa-replacement-project).\n\n## Usage\n\n### Quick start\n\nCheck out the [Quick Start section](https://nemseer.readthedocs.io/en/latest/quick_start.html) in `nemseer`'s documentation.\n\n## Contributing\n\nInterested in contributing? Check out the [contributing guidelines](./CONTRIBUTING.md), which also includes steps to install `nemseer` for development.\n\nPlease note that this project is released with a [Code of Conduct](./CONDUCT.md). By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`nemseer` was created by Abhijith Prakash. It is licensed under the terms of the [BSD 3-Clause license](./LICENSE).\n\n## Credits\n\n`nemseer` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n",
    'author': 'Abhijith Prakash',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
