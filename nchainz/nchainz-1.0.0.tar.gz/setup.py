# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nchainz', 'nchainz.tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'nchainz',
    'version': '1.0.0',
    'description': 'Like 2 Chainz but better!',
    'long_description': '# nchainz - Automatic Method Chaining in Python\nA metaclass for automatic method chaining. (Only for methods that return `None`, obviously)\n\n```python\nfrom nchainz import Chainz\n\nclass A(metaclass=Chainz):\n\n  def has_return_value(self):\n    return 4\n\n  def this_is_chainable(self):\n    print("hello")\n    # implicitly returns self\n\na = A()\nassert a = a.this_is_chainable().this_is_chainable()\nassert a.has_return_value() == 4\n```\n\n\n## What is Method Chaining?\n\n[Method chaining](https://en.wikipedia.org/wiki/Method_chaining) describes the Syntax of not having to assign objects\nbetween methods which are changing the state.\n\nFor example, in JS one can just chain the array transformations like\n\n```JS\n[1,2,3,4,5,6].filter(x => x % 2 == 0).map(x => x * x).find(x => x > 30)\n```\n\n## How to do it manually?\n\nPretty easy. You just return `self`. Here is an example:\n\n```python\nclass MyNum:\n  def __init__(self, x):\n    self.x = x\n  def inc(self):\n    self.x += 1\n    return self\n\nthree = MyNum(3)\nsix = three.inc().inc().inc()\nassert three.x+3 == six.x\n```\n\n## Install\n\n```\npip install nchainz\n```\n\n## Use\n\nJust use the `Chainz` metaclass:\n\n```python\nfrom nchainz import Chainz\n\nclass MyClass(metaclass=Chainz):\n  ...\n```\n\n## Why? Like seriously, Why?\n\nI had my 5 minutes, I am sorry.\n\n## Further reading\n\nIt\'s such a great read, you should really read it. (Written for Python 2)\n\n[Meta-classes Made Easy](https://web.archive.org/web/20200124090402id_/http://www.voidspace.org.uk/python/articles/metaclasses.shtml)\n',
    'author': 'Lars Quentin',
    'author_email': 'lars@lquenti.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lquenti/nchainz',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
