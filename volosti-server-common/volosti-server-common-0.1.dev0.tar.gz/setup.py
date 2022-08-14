# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['volosti_server_common',
 'volosti_server_common.migrations',
 'volosti_server_common.models']

package_data = \
{'': ['*'], 'volosti_server_common': ['static/*', 'templates/base/*']}

install_requires = \
['alembic>=1.8.1,<2.0.0', 'sqlalchemy>=1.4.40,<2.0.0']

extras_require = \
{'all': ['jinja2>=3.1.2,<4.0.0'], 'wui': ['jinja2>=3.1.2,<4.0.0']}

setup_kwargs = {
    'name': 'volosti-server-common',
    'version': '0.1.dev0',
    'description': 'Общий исходный код реализаций сервера Волостей',
    'long_description': 'volosti-server-common\n=====================\nОбщий исходный код реализаций сервера Волостей\n',
    'author': 'Ruslan Ilyasovich Gilfanov',
    'author_email': 'ri.gilfanov@yandex.ru',
    'maintainer': 'Ruslan Ilyasovich Gilfanov',
    'maintainer_email': 'ri.gilfanov@yandex.ru',
    'url': 'https://pypi.org/project/volosti-server-common',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
