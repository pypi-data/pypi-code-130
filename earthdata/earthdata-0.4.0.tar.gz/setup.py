# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['earthdata']

package_data = \
{'': ['*'], 'earthdata': ['css/*']}

install_requires = \
['aiofiles>=0.8.0',
 'aiohttp>=3.8.0',
 'fsspec>=2022.1',
 'multimethod>=1.8',
 'pqdm>=0.1',
 'python-benedict>=0.25',
 'python-cmr>=0.7',
 'requests>=2.26',
 's3fs>=2021.11,<2024',
 'tinynetrc>=1.3.1,<2.0.0']

setup_kwargs = {
    'name': 'earthdata',
    'version': '0.4.0',
    'description': 'Client library for NASA Earthdata APIs',
    'long_description': '# earthdata 🌍\n\n<p align="center">\n    <em>Client library for NASA CMR and EDL APIs</em>\n</p>\n\n<p align="center">\n<a href="https://github.com/betolink/earthdata/actions?query=workflow%3ATest" target="_blank">\n    <img src="https://github.com/betolink/earthdata/workflows/Test/badge.svg" alt="Test">\n</a>\n<a href="https://github.com/betolink/earthdata/actions?query=workflow%3APublish" target="_blank">\n    <img src="https://github.com/betolink/earthdata/workflows/Publish/badge.svg" alt="Publish">\n</a>\n<a href="https://pypi.org/project/earthdata" target="_blank">\n    <img src="https://img.shields.io/pypi/v/earthdata?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/earthdata/" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/earthdata.svg" alt="Python Versions">\n</a>\n<a href="https://github.com/psf/black" target="_blank">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">\n</a>\n\n<a href="https://nsidc.github.io/earthdata/" target="_blank">\n    <img src="https://readthedocs.org/projects/earthdata/badge/?version=latest&style=plastic" alt="Documentation link">\n</a>\n\n\n\n## Overview\n\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/betolink/earthdata/main)\n\nA Python library to search and access NASA datasets.\n\n## Installing earthdata\n\nInstall the latest release:\n\n```bash\nconda install -c conda-forge earthdata\n```\n\nOr you can clone `earthdata` and get started locally\n\n```bash\n\n# ensure you have Poetry installed\npip install --user poetry\n\n# install all dependencies (including dev)\npoetry install\n\n# develop!\n```\n\n## Example Usage\n\n```python\nfrom earthdata import Auth, DataGranules, DataCollections, Store\n\nauth = Auth().login(strategy="netrc") # if we want to access NASA DATA in the cloud\n\n# To search for collecrtions (datasets)\n\nDatasetQuery = DataCollections().keyword(\'MODIS\').bounding_box(-26.85,62.65,-11.86,67.08)\n\ncounts = DatasetQuery.hits()\ncollections = DatasetQuery.get()\n\n\n# To search for granules (data files)\nGranuleQuery = DataGranules().concept_id(\'C1711961296-LPCLOUD\').bounding_box(-10,20,10,50)\n\n# number of granules (data files) that matched our criteria\ncounts = GranuleQuery.hits()\n# We get the metadata\ngranules = GranuleQuery.get(10)\n\n# earthdata provides some convenience functions for each data granule\ndata_links = [granule.data_links(access="direct") for granule in granules]\n\n# or if the data is an on-prem dataset\n\ndata_links = [granule.data_links(access="onprem") for granule in granules]\n\n# The Store class allows to get the granules from on-prem locations with get()\n# NOTE: Some datasets require users to accept a Licence Agreement before accessing them\nstore = Store(auth)\n\n# This works with both, on-prem or cloud based collections**\nstore.get(granules, local_path=\'./data\')\n\n# if you\'re in a AWS instance (us-west-2) you can use open() to get a fileset of S3 files!\nfileset = store.open(granules)\n\n# Given that this is gridded data (Level 3 or up) we could\nxarray.open_mfdataset(fileset, combine=\'by_coords\')\n```\n\nFor more examples see the `Demo` and `EarthdataSearch` notebooks.\n\n\nOnly **Python 3.8+** is supported.\n\n\n## Code of Conduct\n\nSee [Code of Conduct](CODE_OF_CONDUCT.md)\n\n## Level of Support\n\n* This repository is not actively supported by NSIDC but we welcome issue submissions and pull requests in order to foster community contribution.\n\n<img src="docs/nsidc-logo.png" width="84px" />\n\n\n\n## Contributors\n\n[![Contributors](https://contrib.rocks/image?repo=nsidc/earthdata)](https://github.com/nsidc/earthdata/graphs/contributors)\n\n## Contributing Guide\n\nWelcome! 😊👋\n\n> Please see the [Contributing Guide](CONTRIBUTING.md).\n',
    'author': 'Luis Lopez',
    'author_email': 'betolin@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
