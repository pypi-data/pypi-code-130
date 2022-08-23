# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['picsellia_collectstatic',
 'picsellia_collectstatic.management',
 'picsellia_collectstatic.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0,<5.0']

setup_kwargs = {
    'name': 'picsellia-collectstatic',
    'version': '0.0.3',
    'description': 'Optimized collectstatic for S3ManifestStaticStorage',
    'long_description': "# picsellia-s3manifestcollectstatic\nThis is a fork of https://github.com/dduong42/s3manifestcollectstatic\n\nOptimized collectstatic for S3ManifestStaticStorage.\nWith max_workers parameters and custom handler of exception while uploading files\n\n## Installation\n\n1. Install the package\n```\npip install picsellia-s3manifestcollectstatic\n```\n2. Add `picsellias3manifestcollectstatic` to `INSTALLED_APPS`\n\n## Description\n\n`collectstatic` can take a long time. When used with\n`storages.backends.s3boto3.S3ManifestStaticStorage`, `collectstatic` uploads\nthe files twice, once without the hash at the end of the file name, and once\nwith the hash.  Also, it doesn't use multiple threads to upload to s3.\n\n`s3manifestcollectstatic` uploads the files only once, uses threads to speed\nthings up, and doesn't upload the files that are already on S3.\n\ncollectstatic: (Around 20 minutes)\n\n```\n$ time ./manage.py collectstatic --noinput\n\n604 static files copied, 646 post-processed.\n./manage.py collectstatic --noinput  29,94s user 2,27s system 2% cpu 20:25,06 total\n```\n\ns3manifestcollectstatic: (Around 30 seconds)\n```\n$ time ./manage.py s3manifestcollectstatic\n\n604 static files copied to '/tmp/tmpbw0q_5lq', 646 post-processed.\nStart the upload of 604 files\nUploading the manifest\n./manage.py s3manifestcollectstatic  10,95s user 1,92s system 49% cpu 26,269 total\n```\n\nIf you want to reupload the files use `-f`:\n```\n./manage.py s3manifestcollectstatic -f\n```\n\nTested with Python 3.9, Django 3.2, django-storages 1.11\n",
    'author': 'Thomas Darget',
    'author_email': 'thomas.darget@picsellia.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/picselliahq/s3manifestcollectstatic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
