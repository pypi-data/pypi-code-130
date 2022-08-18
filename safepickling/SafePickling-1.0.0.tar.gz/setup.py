# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['safepickling']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'safepickling',
    'version': '1.0.0',
    'description': 'SafePickling is a python library that allows you to sign and verify python pickles',
    'long_description': "# SafePickling\n\nSafePickling is a python library that allows you to sign and verify python pickles.\n\n```mermaid\ngraph LR\n    subgraph Server\n        A[Object]:::object -->B{Pickle and sign}:::cryptography\n        C[Key]:::storage --> B\n        B --> pik2[signature] --> D(Server):::network\n        B --> pik1[pickle] --> D\n    end\n    subgraph Client\n        D ==> E(Client):::network\n        E -->unpik2[signature]\n        E -->unpik1[pickle] --> F{Sign}:::cryptography\n        known[(Known keys)]:::storage --> F --> F\n        F --> eq{Is equal?}\n        unpik2 --> eq:::cryptography\n        eq -->|Yes|unpik{{Unpickle}}:::cryptography --> Z[Object]:::object\n        eq -->|No|Invalid(Invalid):::error\n    end\n\n    classDef network fill:#FFD666;\n    classDef cryptography fill:#82FF66;\n    classDef error fill:#FF6B66;\n    classDef storage fill:#DE66FF;\n    classDef object fill:#666EFF;\n```\n\n## Installation\n\n```sh\npip install safepickling\n```\n\n## Usage Example\n\n```python\nobject = ExampleObject()\n\nserver = SafePickling() # Create a server instance\nserver.generate_key() # Generate a random key for the server\npickled_object = server.pickle(object) # Pickle the object and sign it\n```\n```python\nclient = SafePickling() # Create a client instance\nclient.add_trusted_keys([server.key]) # Add the server's key to the client's trusted keys\nunpickled_object = client.unpickle(pickled_object) # Unpickle the data while verifying it's signature with the server's key\n```\n\n## Cryptography\n\nRandom provided by `secrets.token_bytes`\n\nHash comparison with `hmac.compare_digest`\n\nHashing done using `hashlib.blake2b`\n",
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
