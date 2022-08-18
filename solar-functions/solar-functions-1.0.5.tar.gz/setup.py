# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solar_functions',
 'solar_functions.solar',
 'solar_functions.solar.__solardate__']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'solar-functions',
    'version': '1.0.5',
    'description': 'solar-functions This Module is Designed With Love For Iranian Developers And Programmers By Sami Dev | Telegram: T.me/Sami_Dev',
    'long_description': '.. image:: https://s6.uupload.ir/files/download_9zh5.png\n\n|pypi| |pyversion| |downloads|\n\n.. |pypi| image:: https://img.shields.io/pypi/v/solar_functions.svg\n   :alt: solar_functions PyPI Project Page\n   :target: https://pypi.org/project/solar_functions/\n\n.. |pyversion| image:: https://img.shields.io/pypi/pyversions/solar_functions.svg\n   :alt: Supported Python Versions\n\n.. |downloads| image:: https://static.pepy.tech/badge/solar_functions/month\n   :alt: PyPI Download Count\n   :target: https://pepy.tech/project/solar_functions\n\n.. badges-end\n\n\n\n**Install Module**\n\n::\n\n    $ pip3 install solar_functions\n\n\n\n**Solar Functions**\n\n- Get The Exact **Solar Date**,\n\n- Get The Exact **Solar Time**,\n\n- **High Speed** in Receiving **Date** And **Time**,\n\n\n\n**Get Solar Date**\n\n::\n\n    from solar_functions import solar\n\n    print(solar.date)\n\n\n\n**Get Solar Time**\n\n::\n\n    from solar_functions import solar\n\n    print(solar.time)\n\n\n\n\n**Description**\n\nThis **Module** is Designed For **Iranian developers** And **programmers** By **Sami Dev** so That They Can Easily Get The **Date** And **Solar Time**, Hopefully With This Coding Module it Will Be Easy For **Iranian Developers** And **Programmers**.\n\n\n\n**Thank You For Your Support, Sami Dev**',
    'author': 'Sami Dev',
    'author_email': 'hzsami82@email.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
