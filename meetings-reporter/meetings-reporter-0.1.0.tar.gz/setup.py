# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['meetings_reporter']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'meetings-reporter',
    'version': '0.1.0',
    'description': '',
    'long_description': '|License MIT| |Python 3.7.1|\n\nMeetings reporter\n=================\n\nThis module allows users to parse an input meetings file to find if\nthere are conflicting ones.\n\nInstallation\n------------\n\nRequirements\n~~~~~~~~~~~~\n\n-  Python >= 3.7.1\n-  pandas >= 1.3.5\n\n.. _installation-1:\n\nInstallation\n~~~~~~~~~~~~\n\n``pip install meetings-reporter``\n\nUsage\n-----\n\n::\n\n   >>> from meetings_reporter import *\n    \n   >>> report("FILE_PATH")\n\nIn order to get a coherent meetings report, make sure the input file has\nthe format below:\n\n::\n\n   start,end\n   8:15am,9:30am\n   9:00am,10:00am\n   2:30pm,4:00pm\n\nExample\n~~~~~~~\n\nThe reporting of the file given above\n\n::\n\n   >>> from meetings_reporter import *\n    \n   >>> report("/PATH_TO/ABOVE_FILE_NAME")\n   REPORT: \n    Conflict 1 :  08:15AM--->09:30AM  with  09:00AM--->10:00AM\n\nAuthor\n------\n\n-  Main maintainer: Mohamed Khalil Labidi (mklkun)\n\n.. |License MIT| image:: https://img.shields.io/badge/License-MIT-blue.svg\n.. |Python 3.7.1| image:: https://img.shields.io/badge/python-3.7.1-green.svg\n',
    'author': 'mklkun',
    'author_email': 'mohamed.khalil.labidi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mklkun/meetings-reporter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
