# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['quart_trio', 'quart_trio.testing', 'quart_trio.wrappers']

package_data = \
{'': ['*']}

install_requires = \
['hypercorn[trio]>=0.12.0', 'quart>=0.18', 'trio>=0.9.0']

extras_require = \
{'docs': ['pydata_sphinx_theme']}

setup_kwargs = {
    'name': 'quart-trio',
    'version': '0.10.0',
    'description': 'A Quart extension to provide trio support',
    'long_description': "Quart-Trio\n==========\n\n|Build Status| |docs| |pypi| |python| |license|\n\nQuart-Trio is an extension for `Quart\n<https://gitlab.com/pgjones/quart>`__ to support the `Trio\n<https://trio.readthedocs.io/en/latest/>`_ event loop. This is an\nalternative to using the asyncio event loop present in the Python\nstandard library and supported by default in Quart.\n\nQuickstart\n----------\n\nQuartTrio can be installed via `pip\n<https://docs.python.org/3/installing/index.html>`_,\n\n.. code-block:: console\n\n    $ pip install quart-trio\n\nand requires Python 3.7.0 or higher (see `python version support\n<https://pgjones.gitlab.io/quart/discussion/python_versions.html>`_ for\nreasoning).\n\nA minimal Quart example is,\n\n.. code-block:: python\n\n    from quart import websocket\n    from quart_trio import QuartTrio\n\n    app = QuartTrio(__name__)\n\n    @app.route('/')\n    async def hello():\n        return 'hello'\n\n    @app.websocket('/ws')\n    async def ws():\n        while True:\n            await websocket.send('hello')\n\n    app.run()\n\nif the above is in a file called ``app.py`` it can be run as,\n\n.. code-block:: console\n\n    $ python app.py\n\nTo deploy in a production setting see the `deployment\n<https://pgjones.github.io/quart-trio/tutorials/deployment.html>`_\ndocumentation.\n\nContributing\n------------\n\nQuart-Trio is developed on `GitHub\n<https://github.com/pgjones/quart-trio>`_. You are very welcome to\nopen `issues <https://github.com/pgjones/quart-trio/issues>`_ or\npropose `merge requests\n<https://github.com/pgjones/quart-trio/merge_requests>`_.\n\nTesting\n~~~~~~~\n\nThe best way to test Quart-Trio is with Tox,\n\n.. code-block:: console\n\n    $ pip install tox\n    $ tox\n\nthis will check the code style and run the tests.\n\nHelp\n----\n\nThe `Quart-Trio <https://pgjones.github.io/quart-trio/>`__ and `Quart\n<https://pgjones.github.io/quart/>`__ documentation are the best\nplaces to start, after that try searching `stack overflow\n<https://stackoverflow.com/questions/tagged/quart>`_, if you still\ncan't find an answer please `open an issue\n<https://github.com/pgjones/quart-trio/issues>`_.\n\n\n.. |Build Status| image:: https://github.com/pgjones/quart-trio/actions/workflows/ci.yml/badge.svg\n   :target: https://github.com/pgjones/quart-trio/commits/main\n\n.. |docs| image:: https://img.shields.io/badge/docs-passing-brightgreen.svg\n   :target: https://quart-trio.readthedocs.io\n\n.. |pypi| image:: https://img.shields.io/pypi/v/quart-trio.svg\n   :target: https://pypi.python.org/pypi/Quart-Trio/\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/quart-trio.svg\n   :target: https://pypi.python.org/pypi/Quart-Trio/\n\n.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg\n   :target: https://github.com/pgjones/quart-trio/blob/main/LICENSE\n",
    'author': 'pgjones',
    'author_email': 'philip.graham.jones@googlemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pgjones/quart-trio/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
