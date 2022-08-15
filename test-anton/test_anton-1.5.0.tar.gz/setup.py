# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['test_anton']
setup_kwargs = {
    'name': 'test-anton',
    'version': '1.5.0',
    'description': 'it is mini desc',
    'long_description': '# Collection Framework\n \n**example_package_collection_framework** is a commands-line program that takes a string and returns the number of unique characters in the string.\n\n### Install\n\n```python\npip install -i https://test.pypi.org/simple/ example_package_collection_framework\n```\n\n### How to Use\n\n1. You can use terminal to install some modules.\n```python\npip install argparse\npip install pytest\n```\n\n2. Use this string in terminal to start a program\n```python\npython -m example_package_collection_framework.cli --string [YOUR STRING]\n```\nor\n```python\npython -m example_package_collection_framework.cli --file [YOUR PATH TO FILE]\n```\n\n<br>\n\nSee the source at  [Link](https://git.foxminded.com.ua/foxstudent102894/task-5-create-the-python-package)\n<br>\n© 2022 Anton Skazko',
    'author': 'Skazko Anton',
    'author_email': 'sk.anton06@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
