# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiob2']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'pydantic>=1.9.2,<2.0.0',
 'pytest-asyncio>=0.19.0,<0.20.0']

setup_kwargs = {
    'name': 'aiob2',
    'version': '0.4.2',
    'description': "A simple and easy to use async wrapper for Backblaze's B2 bucket API.",
    'long_description': '# aiob2\n\n---\n\n<p align="center">\n    <a href="https://www.python.org/downloads/">\n        <img src="https://img.shields.io/pypi/pyversions/aiob2?style=for-the-badge" alt="Python Version">\n    </a>\n    <a href="https://github.com/Void-ux/aiob2/actions">\n        <img src="https://img.shields.io/github/workflow/status/Void-ux/aiob2/Build?style=for-the-badge" alt="Build">\n    </a>\n    <a href="https://pypi.org/project/aiob2/">\n        <img src="https://img.shields.io/pypi/v/aiob2?color=8BC34A&style=for-the-badge" alt="PyPi">\n    </a>\n    <a href="https://opensource.org/licenses/MIT">\n        <img src="https://img.shields.io/pypi/l/aiob2?color=C0C0C0&style=for-the-badge" alt="License">\n    </a>\n</p>\n\naiob2 is an asynchronous API wrapper for the [Backblaze B2 Bucket API](https://www.backblaze.com/b2/docs/calling.html).\n\nIt will allow you to interact with your B2 bucket, it\'s files and anything else that the B2 API allows in a modern, object-oriented fashion.\n\n__**NOTE:**__ This API wrapper is by no means *complete* and has many endpoints to cover, though the main ones have been covered (they will be listed below)\n\n# Installation\n\n---\n\naiob2 is compatible with Python 3.8+ (this is an estimate). To install aiob2, run the following command in your (virtual) environment.\n```\npip install aiob2\n```\nAlternatively, for the latest though least stable version, you can download it from the GitHub repo:\n```\npip install git+https://github.com/Void-ux/aiob2.git\n```\n\n# Usage\n\n### Uploading\n```python\nimport aiohttp\nimport asyncio\n\nfrom aiob2 import B2ConnectionInfo, Client\n\n# Construct our connection info\nconn_info = B2ConnectionInfo(\'key_id\', \'app_id\')\n\n# Our image to upload to our bucket\nwith open(r\'C:\\Users\\MS1\\Pictures\\Camera Roll\\IMG_5316.jpeg\', \'rb\') as file:\n    data = file.read()\n\nasync def main():\n    client = Client(conn_info)\n    file = await client.upload_file(\n        content_bytes=data,\n        content_type=\'image/jpeg\',\n        file_name=\'test.jpg\',\n        bucket_id=\'bucket_id\',\n    )\n    await client.close()\n\n\nif __name__ == \'__main__\':\n    asyncio.run(main())\n```\n\nAnd that\'s it! `upload_file()` returns a `File` object that neatly wraps everything Backblaze\'s API has provided us with. The `File` object has the following **attributes**:\n```\n- account_id: str\n- action: str\n- bucket_id: str\n- content_length: int\n- content_sha1: str\n- content_md5: str\n- content_type: str\n- id: str\n- info: dict\n- name: str\n- retention: dict\n- legal_hold: dict\n- server_side_encryption: dict\n- upload_timestamp: datetime.datetime\n```\nYou can visit the [bucket.py](https://github.com/Void-ux/aiob2/blob/master/aiob2/types.py#L15-L29) file to view the source code of this class.\n\n### Deleting\n\n```python\n# We can remove the boilerplate code and get straight to the method\ndeleted_file = await client.delete_file(file_name=\'file_name\', file_id=\'file_id\')\n```\nThis will return a `DeletedFile` object, it has the following **attributes**:\n```\n- name: str\n- id: str\n```\n\n\n### Downloading\nDownloading a file can be done either with the `name` or the `id` of it.\n\n```python\ndownloaded_file = await client.download_file_by_name(file_name=\'file_name\', bucket_name=\'bucket_name\')\n```\n\n```python\ndownloaded_file = await client.download_file_by_id(file_id=\'file_id\')\n```\nThis will return a `DownloadedFile` object with the following attributes:\n```\n- name: str\n- id: str\n- content_sha1: str\n- upload_timestamp: datetime.datetime\n- accept_ranges: str\n- content: bytes\n- content_type: str\n- content_length: str\n- date: str\n```\n**NOTE:** There are many kwargs you can provide when downloading a file, it\'s recommended to take a look at the source \ncode to see if any can benefit you and your usecase.\n\n# License\n\n---\n\nThis project is released under the [MIT License](https://opensource.org/licenses/MIT).',
    'author': 'Dan',
    'author_email': 'the.void.altacc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
