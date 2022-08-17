# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scripts',
 'tests',
 'tests.openquake',
 'tests.scripts',
 'toshi_hazard_store',
 'toshi_hazard_store.model',
 'toshi_hazard_store.oq_import']

package_data = \
{'': ['*'], 'tests': ['fixtures/*', 'fixtures/aggregation/*']}

install_requires = \
['numpy>=1.23.1,<2.0.0',
 'nzshm-common>=0.3.2,<0.4.0',
 'pandas>=1.4.3,<2.0.0',
 'pynamodb-attributes>=0.3.2,<0.4.0',
 'pynamodb>=5.2.1,<6.0.0']

entry_points = \
{'console_scripts': ['get_hazard = scripts.get_hazard:main',
                     'query_meta = scripts.query_meta:main',
                     'store_hazard = scripts.store_hazard:main',
                     'store_hazard_v3 = scripts.store_hazard_v3:main']}

setup_kwargs = {
    'name': 'toshi-hazard-store',
    'version': '0.5.3',
    'description': 'Library for saving and retrieving NZHSM openquake hazard results with convenience (uses AWS Dynamodb).',
    'long_description': '# toshi-hazard-store\n\n\n[![pypi](https://img.shields.io/pypi/v/toshi-hazard-store.svg)](https://pypi.org/project/toshi-hazard-store/)\n[![python](https://img.shields.io/pypi/pyversions/toshi-hazard-store.svg)](https://pypi.org/project/toshi-hazard-store/)\n[![Build Status](https://github.com/GNS-Science/toshi-hazard-store/actions/workflows/dev.yml/badge.svg)](https://github.com/GNS-Science/toshi-hazard-store/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/GNS-Science/toshi-hazard-store/branch/main/graphs/badge.svg)](https://codecov.io/github/GNS-Science/toshi-hazard-store)\n\n\n* Documentation: <https://GNS-Science.github.io/toshi-hazard-store>\n* GitHub: <https://github.com/GNS-Science/toshi-hazard-store>\n* PyPI: <https://pypi.org/project/toshi-hazard-store/>\n* Free software: GPL-3.0-only\n\n## Features\n\n* Main purpose is to upload Openquake hazard results to a DynamodDB tables defined herein.\n* relates the results to the toshi hazard id identifying the OQ hazard job run.\n* extracts metadata from the openquake hdf5 solution\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'GNS Science',
    'author_email': 'chrisbc@artisan.co.nz',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/GNS-Science/toshi-hazard-store',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
