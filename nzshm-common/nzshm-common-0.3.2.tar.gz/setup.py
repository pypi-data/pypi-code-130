# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nzshm_common',
 'nzshm_common.geometry',
 'nzshm_common.grids',
 'nzshm_common.location',
 'nzshm_common.util',
 'tests']

package_data = \
{'': ['*']}

extras_require = \
{'geometry': ['geopandas[geometry]>=0.11.1,<0.12.0']}

setup_kwargs = {
    'name': 'nzshm-common',
    'version': '0.3.2',
    'description': 'A small pure python library for shared NZ NSHM data like locations.',
    'long_description': "# nzshm-common\n\nA pure python library of shared objects used in nzshm projects\n\n## Installation\n\n```\npip install git+https://github.com/GNS-Science/nzshm-common-py>=1.0.0b\n```\n\n## Use\n\n```\n>>> from nzshm_common.location import location\n>>> dir(location)\n['LOCATIONS', 'LOCATION_LISTS', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'location_by_id']\n>>>\n```\n",
    'author': 'GNS Science',
    'author_email': 'chrisbc@artisan.co.nz',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/GNS-Science/nzshm-common-py',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0.0',
}


setup(**setup_kwargs)
