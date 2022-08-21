# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['drebedengi']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=22.1.0,<23.0.0', 'click>=8.1.3,<9.0.0', 'zeep>=4.1.0,<5.0.0']

setup_kwargs = {
    'name': 'drebedengi-python-api',
    'version': '0.1.0',
    'description': 'Python wrapper for Drebedengi SOAP API.',
    'long_description': '# Drebedengi Python API\n\n[![pypi](https://img.shields.io/pypi/v/drebedengi-python-api.svg)](https://pypi.org/project/drebedengi-python-api/)\n[![python](https://img.shields.io/pypi/pyversions/drebedengi-python-api.svg)](https://pypi.org/project/drebedengi-python-api/)\n[![Build Status](https://github.com/mishamsk/drebedengi-python-api/actions/workflows/dev.yml/badge.svg)](https://github.com/mishamsk/drebedengi-python-api/actions/workflows/dev.yml)\n\n\nA rather thin python wrapper for Drebedengi SOAP API.\n\n\n* Documentation: <https://mishamsk.github.io/drebedengi-python-api>\n* GitHub: <https://github.com/mishamsk/drebedengi-python-api>\n* PyPI: <https://pypi.org/project/drebedengi-python-api/>\n* Free software: GPL-3.0-only\n\n\n## Features\n\n* Almost full coverage of "get" methods with better English naming for params & types (see [drebedengi.api][])\n\n!!! important\n    Retrieving aggregated reports via `get_transactions` is not currently supported, despite full list of API parameters\n\n* Typed data model (see [drebedengi.model][])\n\n## Credits\n\nThanks to:\n\n- [drebedengi](https://www.drebedengi.ru/) for a great finance management service\n- [zeep](https://docs.python-zeep.org/en/master/index.html) for a convenient Python SOAP client\n- [lxml](https://lxml.de) for XML library\n- [attrs](https://www.attrs.org/en/stable/index.html) for model classes\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [mishamsk/cookiecutter-pypackage](https://github.com/mishamsk/cookiecutter-pypackage) project template.\n',
    'author': 'Mike Perlov',
    'author_email': 'mishamsk@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mishamsk/drebedengi-python-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
