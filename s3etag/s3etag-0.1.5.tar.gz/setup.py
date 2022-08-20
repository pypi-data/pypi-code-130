# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['s3etag']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['s3etag = s3etag:main']}

setup_kwargs = {
    'name': 's3etag',
    'version': '0.1.5',
    'description': 'Compute AWS S3 Etags',
    'long_description': '```text\nusage: s3etag [-h] [--chunksize size] files [files ...]\n\ns3etag - compute AWS S3 Etags\n\npositional arguments:\n  files             filenames\n\noptional arguments:\n  -h, --help        show this help message and exit\n  --chunksize size  multipart_chunksize used for upload in bytes or with a\n                    size suffix KB, MB, GB, or TB (default: 8MB)\n```\n',
    'author': 'LiosK',
    'author_email': 'contact@mail.liosk.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/LiosK/s3etag',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
