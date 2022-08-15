# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['amazon_sp_api_clients']

package_data = \
{'': ['*']}

install_requires = \
['boto3', 'cachetools', 'chardet', 'peewee', 'pycryptodome', 'requests']

setup_kwargs = {
    'name': 'amazon-sp-api-clients',
    'version': '1.8.6',
    'description': 'Amazon selling partner api clients.',
    'long_description': '# amazon-sp-api-clients\n\nThis is a package generated from amazon selling partner open api models.\n\nThe package is tested in many situations, with fully type hint supported. Enjoy it! \n\n![typehint 1](./docs/source/typehint1.png)\n\n![typehint 2](./docs/source/typehint2.png)\n\n![typehint 3](./docs/source/typehint3.png)\n\n## Attention\n\nV1.0.0 changes many api, compared with v0.x.x!\n\n注意！V1.0.0相较于v0.x.x更改了大量的API！\n\n## Features\n\n* ready to use;\n* provide code to generate clients, in case that amazon update models;\n* type hint;\n* orders api, feed api, report api, and all other apis;\n* automatically manage tokens.\n\n## Installation\n\n```shell\npip install amazon-sp-api-clients\n```\n\n## Note\n\nFor technical support, please contact [panhaoyu.china@outlook.com](mailto:panhaoyu.china@outlook.com).\n\nPreviously this lib is only open access but not open source, and now it\'s time to make it public to serve more developers.\n\nIf there\'s any bug, please fell free to open an issue or send a pr.\n\n## Usage\n\nFor saving time, I just paste part of my test code here as a demo.\n\nFor better understanding, all the fields are the same length of actual fields, and some readable information are kept.\n\n```python\nfrom datetime import datetime\nimport amazon_sp_api_clients\nendpoint = "https://sellingpartnerapi-eu.amazon.com"\nmarketplace_id = "XXXXXXXXXXXXXX"\nrefresh_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\nrole_arn = "arn:aws:iam::123456789012:role/xxxxxx"\naws_access_key = \'XXXXXXXXXXXXXXXXXXXX\'\naws_secret_key = "XXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"\nclient_id = \'amzn1.application-oa2-client.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\'\nclient_secret = \'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\'\nclient_config = dict(\n    role_arn=role_arn,\n    endpoint=endpoint,\n    marketplace_id=marketplace_id,\n    refresh_token=refresh_token,\n    aws_access_key=aws_access_key,\n    aws_secret_key=aws_secret_key,\n    lwa_client_key=client_id,\n    lwa_client_secret=client_secret,\n)\nclients = amazon_sp_api_clients.AmazonSpApiClients(**client_config)\norders = clients.orders_v0.getOrders(\n    MarketplaceIds=[marketplace_id],\n    CreatedAfter=datetime(2000, 1, 1).isoformat()\n).payload.Orders\nfor order in orders:\n    print(order.AmazonOrderId, order.LastUpdateDate)\n```\n\n## Configuration\n\nThe client configuration can be set both at the initiation and as environment variables.\n\n* SP_API_ROLE_ARN\n* SP_API_ENDPOINT\n* SP_API_REGION\n* SP_API_MARKETPLACE_ID\n* SP_API_REFRESH_TOKEN\n* SP_API_AWS_ACCESS_KEY\n* SP_API_AWS_SECRET_KEY\n* SP_API_LWA_CLIENT_KEY\n* SP_API_LWA_CLIENT_SECRET\n\n## Build\n\nThe client is generated in the following steps:\n\n1. download amazon open api repository;\n1. copy open api 2 json files from the amazon repository to a single directory;\n1. convert open api 2 json files to open api 3 json files;\n1. convert open api 3 json files to py clients.\n\nThe main script of generation is the `test_main` python file.\n\nWhen convert open api to py clients, I separated the process into 6 steps, which are defined in\nthe `swager_client_generator.stages` module.\n\nIf my build is not suitable for your demand, or amazon api model updates but my build do not follow, you can clone this\nrepo, modify the `api.pyt` template and build it by yourself, and please push a PR, thanks!\n\n# Acknowledgement\n\nThe auth method is partially from\n[python-amazon-sp-api](https://github.com/saleweaver/python-amazon-sp-api).\n\n# Note\n\nIf this library helps you, please give me a star, thanks!\n\n如果这个库对您有用，请为我点亮Star，谢谢！\n',
    'author': 'Haoyu Pan',
    'author_email': 'panhaoyu.china@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
