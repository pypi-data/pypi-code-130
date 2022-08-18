# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edwardsserial', 'edwardsserial.tic']

package_data = \
{'': ['*']}

install_requires = \
['pyserial>2.5.0']

setup_kwargs = {
    'name': 'edwardsserial',
    'version': '0.3.3',
    'description': 'Python API implementing the serial protocoll from edwards vacuum.',
    'long_description': '# edwardsserial\n\n`edwardsserial` is a Python package with an object-oriented wrapper for the [TIC Turbo- and Instrument Controller](https://shop.edwardsvacuum.com/products/d39722000/view.aspx) from Edwards.\n\n## Documentation\n- documentation of the [latest realease](https://codingcoffeebean.gitlab.io/edwardsserial/edwardsserial.html)\n\n## Contributing\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.\n\nA detailed overview on how to contribute can be found in the [contributing guide](CONTRIBUTING.md).\n\n## License\nThis code is licensed under the [MIT license](https://opensource.org/licenses/MIT). See [LICENSE](LICENSE).\n\n## Changelog\nChanges to the code are documented in the [changelog](CHANGELOG.md).\n',
    'author': 'codingcoffeebean',
    'author_email': 'contact@codingcoffeebean.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/codingcoffeebean/edwardsserial',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
