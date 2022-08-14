# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['safepickling']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'safepickling',
    'version': '0.1.2',
    'description': 'SafePickling is a python library that allows you to sign and verify python pickles',
    'long_description': "# SafePickling\n\nSafePickling is a python library that allows you to sign and verify python pickles.\n\n## Installation\n\n`pip install safepickling`\n\n## Usage Example\n\n```python\nobject = ExampleObject()\n\nserver = SafePickling() # Create a server instance\nserver.generate_key() # Generate a random key for the server\nsafe_data = server.pickle(object) # Pickle the object and sign it\n\nclient = SafePickling() # Create a client instance\nclient.add_trusted_keys([server.key]) # Add the server's key to the client's trusted keys\nclient_data = client.unpickle(safe_data) # Unpickle the data while verifying it's signature with the server's key\n```\n\n## Cryptography\n\nRandom provided by `secrets.token_bytes`\nHash comparison with `hmac.compare_digest`\nHashing done using `hashlib.blake2b`\n",
    'author': 'Wissotsky',
    'author_email': 'Wissotsky@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
