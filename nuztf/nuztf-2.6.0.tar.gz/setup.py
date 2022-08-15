# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nuztf']

package_data = \
{'': ['*'], 'nuztf': ['data/*']}

install_requires = \
['ampel-ztf==0.8.2a7',
 'ampel>=0.8.2-alpha.0,<0.9.0',
 'astropy-healpix>=0.6,<0.7',
 'astropy>=5.1,<6.0',
 'astroquery>=0.4.6,<0.5.0',
 'backoff>=1.11.1,<2.0.0',
 'black>=22.6.0,<23.0.0',
 'coveralls>=3.3.1,<4.0.0',
 'geopandas>=0.11.0,<0.12.0',
 'gwemopt>=0.0.76,<0.0.77',
 'healpy>=1.16.0,<2.0.0',
 'ipykernel>=6.15.1,<7.0.0',
 'jupyter>=1.0.0,<2.0.0',
 'lalsuite>=7.5,<8.0',
 'ligo-gracedb>=2.7.7,<3.0.0',
 'ligo.skymap>=1.0.0,<2.0.0',
 'lxml>=4.9.1,<5.0.0',
 'matplotlib>=3.5.2,<4.0.0',
 'mocpy>=0.11.0,<0.12.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pre-commit>=2.20.0,<3.0.0',
 'python-ligo-lw>=1.8.1,<2.0.0',
 'pyvo>=1.3,<2.0',
 'requests>=2.28.1,<3.0.0',
 'scipy>=1.8.1,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'setuptools>=63.2.0,<64.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'wget>=3.2,<4.0',
 'ztfquery>=1.18.4,<2.0.0']

setup_kwargs = {
    'name': 'nuztf',
    'version': '2.6.0',
    'description': 'Package for multi-messenger correlation searches with ZTF',
    'long_description': '# NuZTF\nPython package for correlating ZTF data with external multi-messenger triggers, created by [@robertdstein](https://github.com/robertdstein).\nThis package enables ZTF follow-up analysis of neutrinos/gravitational waves/gamma-ray bursts, built using the [AMPEL platform](https://arxiv.org/abs/1904.05922).\n\n[![DOI](https://zenodo.org/badge/193068064.svg)](https://zenodo.org/badge/latestdoi/193068064)\n[![CI](https://github.com/desy-multimessenger/nuztf/actions/workflows/continous_integration.yml/badge.svg)](https://github.com/desy-multimessenger/nuztf/actions/workflows/continous_integration.yml)\n[![PyPI version](https://badge.fury.io/py/nuztf.svg)](https://badge.fury.io/py/nuztf)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/desy-multimessenger/nuztf/master)\n[![Coverage Status](https://coveralls.io/repos/github/desy-multimessenger/nuztf/badge.svg?branch=master)](https://coveralls.io/github/desy-multimessenger/nuztf?branch=master)\n\n## Installation Instructions\n\nNuZTF can be directly installed with pip, giving the latest stable release:\n\n```pip install nuztf```\n\nAlternatively, the latest Github version of the code can be installed via pip:\n\n```git clone https://github.com/desy-multimessenger/nuztf.git```\n\n```pip install -e nuztf```\n\nIn case you encounter problems with an ARM-based Mac, use conda and issue:\n```conda install -c conda-forge python-confluent-kafka fiona pyproj lalsuite ligo.skymap -y```\nThis should take care of all packages that have not yet been ported.\n\nYou will need the [IRSA login details](https://irsa.ipac.caltech.edu/account/signon/logout.do) with a ZTF-enabled account to fully utilise all features.\n\nAdditionally, you need an AMPEL API token. This can be obtained [here](https://ampel.zeuthen.desy.de/live/dashboard/tokens).\n\n# Citing the code\n\nIf you make use of this code, please cite it! A DOI is provided by Zenodo, which can reference both the code repository, or specific releases:\n\n[![DOI](https://zenodo.org/badge/193068064.svg)](https://zenodo.org/badge/latestdoi/193068064)\n\n# Contributors\n\n* Jannis Necker [@JannisNe](https://github.com/jannisne)\n* Simeon Reusch [@simeonreusch](https://github.com/simeonreusch)\n* Robert Stein [@robertdstein](https://github.com/robertdstein)\n\n# Acknowledgements\n\nThis code stands on the shoulders of giants. We would particularly like to acknowledge:\n\n* [Ampel](https://ampelproject.github.io/), created primarily by [@wombaugh](https://github.com/wombaugh), [@vbrinnel](https://github.com/vbrinnel) and [@jvansanten](https://github.com/jvansanten)\n* [ztf_plan_obs](https://github.com/simeonreusch/ztf_plan_obs), created by [@simeonreusch](https://github.com/simeonreusch)\n* [ztfquery](https://github.com/MickaelRigault/ztfquery), created by [@MickaelRigault](https://github.com/MickaelRigault)\n',
    'author': 'Robert Stein',
    'author_email': 'rdstein@caltech.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/desy-multimessenger/nuztf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
