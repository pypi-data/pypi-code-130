# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['azure_ddns']

package_data = \
{'': ['*']}

install_requires = \
['azure-identity>=1.10.0,<2.0.0', 'azure-mgmt-dns>=8.0.0,<9.0.0']

entry_points = \
{'console_scripts': ['azure-ddns = azure_ddns.cli:main']}

setup_kwargs = {
    'name': 'azure-ddns',
    'version': '0.0.3',
    'description': '',
    'long_description': '# Azure Dynamic DNS\n\n## Installation\n\npip install azure-ddns\n\n## Run\n\nYou can run the cli tool with all the parameters like this\n\n```cmd\nazure-ddns --subscription-id your_ubscription_id --tenant-id your_tenant_id --client-id your_client_id --client-secret your_client_secret --resource-group your_ressource_group_name --zone your_zone_name --record your_record-name\n```\n\nYou can also use a json file\n\n```cmd\nazure-ddns --config path/to/your/config.json\n```\n\nThe json should be formated like this:\n\n```json\n{\n    "subscriptionId": "",\n    "resourceGroup": "",\n    "zoneName": "",\n    "recordName": "",\n    "clientId": "",\n    "clientSecret": "",\n    "tenantId": ""\n}\n```',
    'author': 'tle06',
    'author_email': 'tle@tlnk.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tle06/azure-ddns',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
