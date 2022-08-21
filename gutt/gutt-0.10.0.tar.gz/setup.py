# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['gutt', 'gutt.cli']

package_data = \
{'': ['*']}

install_requires = \
['asttrs>=0.7.0,<0.8.0', 'black', 'click', 'isort']

entry_points = \
{'console_scripts': ['gutt = gutt.cli.main:main']}

setup_kwargs = {
    'name': 'gutt',
    'version': '0.10.0',
    'description': 'Auto generate unit test templates',
    'long_description': "![](https://github.com/ryanchao2012/gutt/actions/workflows/gutt-run-unittests.yml/badge.svg)\n![](https://img.shields.io/pypi/v/gutt.svg)\n![](https://img.shields.io/pypi/pyversions/gutt)\n![](https://img.shields.io/github/license/ryanchao2012/gutt)\n\n# gutt\nAuto Generate Unit Test Templates\n\n\n## Install\n\n```\n$ pip install gutt\n```\n\n\n## Basic Usage\n\nAssume you have a package, and its layout:\n\n```\nmy_awesome_package\n├── __init__.py\n└── module1.py\n```\n\nsome codes inside `my_awesome_package/module1.py`:\n\n```python\n\nimport sys\n\nMY_CONST = 123\n\ndef funcion1():\n    pass\n\n\ndef function2():\n    pass\n\n\nclass MyObject:\n    def method1(self):\n        pass\n\n    @classmethod\n    def classmethod1(cls):\n        pass\n\n    @staticmethod\n    def staticmethod1():\n        pass\n\n```\n\n`gutt` can generate unit testing templates for all implementations in just one line:\n\n```\n$ gutt -m my_awesome_package -o mytests\n```\n\nThe output layout:\n\n```\nmytests\n├── __init__.py\n└── my_awesome_package\n    ├── __init__.py\n    └── test_module1.py\n\n```\n\nThe unit test templates inside `test_module1.py`\n\n```python\ndef test_funcion1():\n    from my_awesome_package.module1 import funcion1\n\n    assert funcion1\n\n\ndef test_function2():\n    from my_awesome_package.module1 import function2\n\n    assert function2\n\n\nclass TestMyObject:\n    @classmethod\n    def setup_class(cls):\n        from my_awesome_package.module1 import MyObject\n\n        assert MyObject\n\n    @classmethod\n    def teardown_class(cls):\n        pass\n\n    def setup_method(self, method):\n        pass\n\n    def teardown_method(self, method):\n        pass\n\n    def test_method1(self):\n        pass\n\n    def test_classmethod1(self):\n        pass\n\n    def test_staticmethod1(self):\n        pass\n\n```\n\nEach module in source codes maps to a testing module(`module1.py --> test_module1.py`), and each function, each class and all methods inside that class maps to corresponding test templates. \n\n- `gutt` will skip code generation if the test templates for the functions already exist.\n- `gutt` won't delete the corresponding test templates if the source codes get deleted or renamed.\n- For new added codes: modules, functions or methods inside class, just re-run `gutt` to generate new test templates for them.\n\n\nRun unit test with `pytest`, for example:\n\n```\n$ pytest --doctest-modules --cov=my_awesome_package mytests\n\n=============================== test session starts ===============================\nplatform linux -- Python 3.8.8, pytest-4.6.11, py-1.10.0, pluggy-0.13.1\nrootdir: /home/ryan/Workspace/my_awesome_package\nplugins: mock-1.13.0, cov-2.11.1\ncollected 5 items                                                                 \n\nmytests/my_awesome_package/test_module1.py .....                            [100%]\n\n----------- coverage: platform linux, python 3.8.8-final-0 -----------\nName                             Stmts   Miss  Cover\n----------------------------------------------------\nmy_awesome_package/__init__.py       0      0   100%\nmy_awesome_package/module1.py       13      5    62%\n----------------------------------------------------\nTOTAL                               13      5    62%\n\n\n============================ 5 passed in 0.07 seconds =============================\n```",
    'author': 'Ryan',
    'author_email': 'ryanchao2012@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ryanchao2012/gutt',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
