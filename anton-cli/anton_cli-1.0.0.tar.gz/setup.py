# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anton_cli']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'anton-cli',
    'version': '1.0.0',
    'description': 'Returns the number of unique characters in the string',
    'long_description': "# Collection Framework\n \n**anton_cli** is a commands-line program that takes a string and returns the number of unique characters in the string.\n\n### Install\n\n```python\npip install anton-cli\n```\n\n### How to Use\n```python\nfrom anton_cli import split_letters, read_from_file\n\nprint(split_letters('hello')) # 3\n```\nalso you can get a unique numbers of string from the file\n\n```python\nprint(read_from_file('words.txt')) # SOME RESULT\n```\n\n\n### Launch\n\nYou can use this program from the terminal\n\nif you want to pass a string use --string [YOUR STRING]\n```python\npython -m anton_cli.cli --string [YOUR STRING]\n```\nor if you want to pass a file use --file [YOUR FILE PATH]\n```python\npython -m anton_cli.cli --file [YOUR PATH TO FILE]\n```\n\n<br>\n\nSee the source at  [Link](https://git.foxminded.com.ua/foxstudent102894/task-5-create-the-python-package)\n<br>\n© 2022 Anton Skazko",
    'author': 'Skazko Anton',
    'author_email': 'sk.anton06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
