# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['datastation', 'datastation.scripts']

package_data = \
{'': ['*']}

install_requires = \
['dicttoxml>=1.7.4,<2.0.0',
 'lxml>=4.8.0,<5.0.0',
 'psycopg>=3.0.16,<4.0.0',
 'pyYAML>=6.0,<7.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['dv-fix-provenance-files = '
                     'datastation.scripts.fix_provenance_files:main',
                     'dv-import-users = datastation.scripts.import_user:main',
                     'dv-prestage-files = '
                     'datastation.scripts.prestage_files:main',
                     'update-datacite-records = '
                     'datastation.scripts.update_datacite_records:main']}

setup_kwargs = {
    'name': 'dans-datastation-tools',
    'version': '0.7.0',
    'description': 'Command line utilities for Data Station application management',
    'long_description': None,
    'author': 'DANS-KNAW',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
