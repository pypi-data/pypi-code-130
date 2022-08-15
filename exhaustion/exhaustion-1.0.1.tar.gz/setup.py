# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exhaustion']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'exhaustion',
    'version': '1.0.1',
    'description': 'A tiny library to help in exhaustive testing of Boolean functions in Python.',
    'long_description': '# exhaustion\nA tiny library to help in exhaustive testing of Boolean functions in Python.\n\n![Logo](logo.svg)\n\n## Requirements\n\n- Python 3.6 or newer\n\n## Installation\n\nExhaustion can be installed using `pip`:\n\n```sh\npip install exhaustion\n```\n\n## Usage\n\nUsage is very straightforward, `exhaustion` is compatible with any testing library that supports assertions.\n\n```python\nimport unittest\n\nfrom exhaustion import exhaust\n\ndef _and(a: bool, b: bool):\n    """ A simple wrapper over the Python `and` operator for demonstration purposes.\n\n    Args:\n        a (bool): The left-hand operand.\n        b (bool): The right-hand operand.\n    Returns:\n        bool: The Boolean conjunction of the arguments provided.\n    """\n    return a and b\n\nclass TestAndAlgebraic(unittest.TestCase):\n    """ Tests the algebraic properties of the _and function.\n    """\n\n    def test_and_commutative(self):\n        """ Proves by exhaustion that the _and function is commutative.\n        """\n        # The lambda below will execute for every possible combination of Boolean arguments.\n        exhaust(lambda a, b: self.assertTrue(_and(a, b) == _and(b, a)))\n```\n\n## Related Projects\n\nThis library is intentionally very minimal, and was designed to be so. If you\'re looking for a richer feature set, you might consider the following projects:\n\n- [exhaust](https://github.com/letmaik/exhaust) - Not to be confused with this project, a library that supports exhastive enumeration of any finite set you can express using a generator function.\n\n## License\n\n[MIT](LICENSE) © [lambdacasserole](https://github.com/lambdacasserole).\n',
    'author': 'Saul Johnson',
    'author_email': 'saul.a.johnson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lambdacasserole/exhaustion.git',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
