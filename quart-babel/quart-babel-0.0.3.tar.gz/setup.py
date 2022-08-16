# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quart_babel', 'quart_babel.utils']

package_data = \
{'': ['*']}

install_requires = \
['Babel>=2.10.3,<3.0.0',
 'ipapi>=1.0.4,<2.0.0',
 'nest-asyncio>=1.5.5,<2.0.0',
 'quart>=0.18.0,<0.19.0']

setup_kwargs = {
    'name': 'quart-babel',
    'version': '0.0.3',
    'description': 'Implements i18n and l10n support for Quart.',
    'long_description': '# Quart Babel\n\n![Quart Uploads Logo](logos/logo.png)\n\nImplements i18n and l10n support for Quart.  This is based on the Python\n[babel][] module as well as [pytz][] both of which are installed automatically\nfor you if you install this library.\n\nThe original code for this extension was taken from Flask-Babel and Flask-BabelPlus. \nFlask-Babel can be found [here][flask-babel] and Flask-BabelPlus can be found \n[here][flask-babelplus]\n\n# Installation \n\nInstall the extension with the following command:\n\n    $ pip3 install quart-babel\n\n# Usage\n\nTo use the extension simply import the class wrapper and pass the Quart app \nobject back to here. Do so like this:\n\n    from quart import Quart\n    from quart_babel import Babel \n\n    app = Quart(__name__)\n    babel = Babel(app)\n\n\n# Documention\n\nThe for Quart-Babel and is available [here][docs].\n\n[babel]: https://github.com/python-babel/babel\n[pytz]: https://pypi.python.org/pypi/pytz/\n[flask-babel]: https://flask-babel.tkte.ch/\n[flask-babelplus]: https://github.com/sh4nks/flask-babelplus\n[docs]: https://flask-babel.tkte.ch/',
    'author': 'Chris Rood',
    'author_email': 'quart.addons@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quart-Addons/quart-uploads',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
