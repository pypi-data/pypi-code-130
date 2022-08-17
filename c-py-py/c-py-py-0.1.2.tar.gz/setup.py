# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['cpp']

package_data = \
{'': ['*']}

install_requires = \
['invoke-iife>=1.1.0,<2.0.0', 'typing-extensions>=4.3.0,<5.0.0']

setup_kwargs = {
    'name': 'c-py-py',
    'version': '0.1.2',
    'description': '',
    'long_description': '# C-Py-Py\n\n```python\nfrom cpp import *\n\nx = (cpp)[std::vector<int>v({1, 2, 3})]\nx.push_back(4)\n(cpp)[std::cout] << "Vector x: " << x << (cpp)[std::endl]\n# -> prints \'Vector x: [1, 2, 3]\'\nfor i in auto& x:\n    (cpp)[std::cout] << "Incrementing " << i << "..." << (cpp)[std::endl]\n    # -> prints \'Incrementing 1...\', \'Incrementing 2...\', etc.\n    i += 1\n\n(cpp)[std::cout] << "Vector after: " << x << (cpp)[std::endl]\n# -> prints \'Vector after: [2, 3, 4, 5]\'\n```\n\n## How?\n\n### Template notation\n\nThe `<>` template notation was quite difficult to pull off. Python has a weird concept of multiple-boolean-operators, so the following:\n\n```python\nx = (cpp)[std::vector<int>v({1, 2, 3})]\n```\n\nis equivalent to\n\n```python\nx = (cpp)[std::((vector < int) and (int > v({1, 2, 3})))]\n```\n\nWe can then overwrite the less than operator for the object `vector` to simply return True, so that it\'s negligible:\n\n```python\nx = (cpp)[std::(True and (int > v({1, 2, 3})))]\nx = (cpp)[std::(int > v({1, 2, 3}))]\n```\n\nNow we can overwrite the less than operator on a different class (`v`, in this case) so that it simply takes in a fully formed vector object as `self` and a type as the comparison, then tries to transform that into a new vector of the type in the comparison. This would be equivalent to:\n\n```python\nx = (cpp)[std::(v({1, 2, 3}))]\n```\n\n### C++-style namespacing\n\nNearly there. For the namespacing (`::`), we turn to the only place in the Python syntax where adjacent colons are allowed: slice notation. The code above is equivalent to:\n\n```python\nx = cpp[slice(std, None, v({1, 2, 3}))]\n```\n\nWe can define `cpp` to be an instance of a class that overrides the `__getitem__` method to simply return the rightmost part of the slice:\n\n```python\nclass cpp:\n    def __getitem__(self, other: slice):\n        return other.step\ncpp = cpp()\n```\n\nNow the code is equivalent to just:\n\n```python\nx = v({1, 2, 3})\n```\n\nwhere `v` is essentially a thin wrapper around `list`.\n\n### cout\n\n`cout` performs a small sleight-of-hand. Since Python is evaluated left-to-right, we have to have the `<<` operator reduce each of the expressions down into a single format string, then pass that to `endl` to actually do the printing. We do this by making `cout`.__lshift__() return a `Coutable`:\n\n```python\nclass _Coutable:\n    def __init__(self, o) -> None:\n        self._total_str: str = format(o)\n\n    def __lshift__(self, other: Any) -> Self:\n        if other is endl:\n            print(self._total_str)\n        self._total_str = self._total_str + format(other)\n        return self\n```\n\nThis class will just keep accumulating objects\' formatted representations until it hits endl, when it will print everything out.\n\n### Taking references\n\nUnfortunately, Python\'s `for _ in _:` syntax is pretty rigid, and won\'t allow any operations in-between for and in, so we have to stick the `auto&` on the right side. This \n\n## Why?\n\nScientists are hard at work trying to come up with an answer to that question.\n',
    'author': 'torshepherd',
    'author_email': 'tor.aksel.shepherd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
