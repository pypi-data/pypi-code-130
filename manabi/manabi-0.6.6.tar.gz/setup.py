# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'manabi_django'}

packages = \
['manabi', 'manabi_migrations', 'manabi_migrations.migrations']

package_data = \
{'': ['*']}

install_requires = \
['WsgiDAV>=4.0.1,<5.0.0',
 'attrs>=22.1.0,<23.0.0',
 'django>=3.2.14,<4.0.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pybase62>=0.5.0,<0.6.0',
 'pybranca>=0.5.0,<0.6.0',
 'types-psycopg2>=2.9.16,<3.0.0']

setup_kwargs = {
    'name': 'manabi',
    'version': '0.6.6',
    'description': 'Provide WebDAV access for documents.',
    'long_description': '# Manabi\n\n## Install\n\nMake sure libsodium exists on the system, for example execute:\n\n```bash\napk add --no-cache libsodium\napt-get install -y libsodium23\n```\n\n# Dev\n\nEnable dev-env:\n\n```bash\npyenv install 3.10.2\npoetry env use $HOME/.pyenv/versions/3.10.2/bin/python3.10\npoetry install\npoetry shell\ndocker-compose up -d db\n(cd manabi_django && ./manage.py migrate manabi_migrations)\n```\n\n## Config\n\nCall `manabi-keygen` and add the key to `config["manabi"]["key"]`. The key is\nshared between the caluma/alexandria backend and the WebDAV server.\n\n`mount_path`\n\nPrefix that gets passed to wsgidav, if URL rewrites remove any prefixes use `"/"`\n\n`lock_storage`\n\nThe ManabiLockLockStorage forces the WebDav log-timeout to `token-refresh-time / 2`\n\n`provider_mapping`\n\nExtends the FilesystemProvider any will only serve files if the token is valid\n\n`middleware_stack`\n\nBased on the default middleware_stack but HTTPAuthenticator is replace by\nManabiAuthenticator, which validates the tokens.\n\n`manabi.key`\n\nShared-key between the server that creates tokens to grant access and wsgi-dav\n\n`manabi.refresh`\n\nHow often tokens are refreshed in seconds, we recommend 10 minutes: `600`\n\n`manabi.initial`\n\nThe time from the token being generated till it has to be refreshed the first\ntime, we recommend 1 minues: `60`. In case tokens leak, for example via cache on\na computer, tokens should be expired by the time an adversary gets them.\n\n```python\nfrom manabi import ManabiDAVApp\n\npostgres_dsn = "dbname=manabi user=manabi host=localhost password=manabi"\nconfig = {\n    "mount_path": "/dav",\n    "lock_storage": ManabiDbLockStorage(refresh, postgres_dsn),\n    "provider_mapping": {\n        "/": ManabiProvider(settings.MEDIA_ROOT),\n    },\n    "middleware_stack": [\n        WsgiDavDebugFilter,\n        ErrorPrinter,\n        ManabiAuthenticator,\n        WsgiDavDirBrowser,\n        RequestResolver,\n    ],\n    "manabi": {\n        "key": key,\n        "refresh": refresh,\n        "initial": settings.MANABI_TOKEN_ACTIVATE_TIMEOUT,\n    },\n}\ndav_app = ManabiDAVApp(config)\n```\n',
    'author': 'Adfinis AG',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/projectcaluma/manabi',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
