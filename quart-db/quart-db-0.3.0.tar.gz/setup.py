# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['quart_db']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.25.0', 'buildpg>=0.4', 'quart>=0.16.3']

extras_require = \
{':extra == "erdiagram"': ['eralchemy2>=1.3.2', 'psycopg2>=2.9.3'],
 'docs': ['pydata_sphinx_theme']}

setup_kwargs = {
    'name': 'quart-db',
    'version': '0.3.0',
    'description': 'Quart-DB is a Quart extension that provides managed connection(s) to postgresql database(s).',
    'long_description': 'Quart-DB\n========\n\n|Build Status| |docs| |pypi| |python| |license|\n\nQuart-DB is a Quart extension that provides managed connection(s) to\npostgresql database(s).\n\nQuickstart\n----------\n\nQuart-DB is used by associating it with an app and a DB (via a URL)\nand then utilising the ``g.connection`` connection,\n\n.. code-block:: python\n\n   from quart import g, Quart, websocket\n   from quart_db import QuartDB\n\n   app = Quart(__name__)\n   db = QuartDB(app, url="postgresql://user:pass@localhost:5432/db_name")\n\n   @app.get("/<int:id>")\n   async def get_count(id: int):\n       result = await g.connection.fetch_val(\n           "SELECT COUNT(*) FROM tbl WHERE id = :id",\n           {"id": id},\n       )\n       return {"count": result}\n\n   @app.post("/")\n   async def set_with_transaction():\n       async with g.connection.transaction():\n           await db.execute("UPDATE tbl SET done = $1", [True])\n           ...\n       return {}\n\n   @app.get("/explicit")\n   async def explicit_usage():\n        async with db.connection() as connection:\n            ...\n\nParameters can be defined via positional ``$1`` or keyword ``:id``\nbinds.\n\nContributing\n------------\n\nQuart-DB is developed on `GitHub\n<https://github.com/pgjones/quart-db>`_. If you come across an issue,\nor have a feature request please open an `issue\n<https://github.com/pgjones/quart-db/issues>`_. If you want to\ncontribute a fix or the feature-implementation please do (typo fixes\nwelcome), by proposing a `merge request\n<https://github.com/pgjones/quart-db/merge_requests>`_.\n\nTesting\n~~~~~~~\n\nThe best way to test Quart-DB is with `Tox\n<https://tox.readthedocs.io>`_,\n\n.. code-block:: console\n\n    $ pip install tox\n    $ tox\n\nthis will check the code style and run the tests.\n\nHelp\n----\n\nThe Quart-DB `documentation\n<https://quart-db.readthedocs.io/en/latest/>`_ is the best places to\nstart, after that try searching `stack overflow\n<https://stackoverflow.com/questions/tagged/quart>`_ or ask for help\n`on gitter <https://gitter.im/python-quart/lobby>`_. If you still\ncan\'t find an answer please `open an issue\n<https://github.com/pgjones/quart-db/issues>`_.\n\n\n.. |Build Status| image:: https://github.com/pgjones/quart-db/actions/workflows/ci.yml/badge.svg\n   :target: https://github.com/pgjones/quart-db/commits/main\n\n.. |docs| image:: https://readthedocs.org/projects/quart-db/badge/?version=latest&style=flat\n   :target: https://quart-db.readthedocs.io/en/latest/\n\n.. |pypi| image:: https://img.shields.io/pypi/v/quart-db.svg\n   :target: https://pypi.python.org/pypi/Quart-DB/\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/quart-db.svg\n   :target: https://pypi.python.org/pypi/Quart-DB/\n\n.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg\n   :target: https://github.com/pgjones/quart-db/blob/main/LICENSE\n',
    'author': 'pgjones',
    'author_email': 'philip.graham.jones@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pgjones/quart-db/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
