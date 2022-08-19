# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipertool']

package_data = \
{'': ['*']}

extras_require = \
{'docs': ['sphinx>=5.1,<6.0',
          'sphinx-autodoc-typehints>=1.19,<2.0',
          'm2r2>=0.3,<0.4',
          'tomlkit>=0.11,<0.12']}

setup_kwargs = {
    'name': 'pipertool',
    'version': '0.0.2',
    'description': 'Piper is an open-source platform for data science and machine learning prototyping.',
    'long_description': '# pipertool\n\n[![Build Status](https://github.com/TatraDev/pipertool/workflows/test/badge.svg?branch=master&event=push)](https://github.com/TatraDev/pipertool/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/TatraDev/pipertool/branch/master/graph/badge.svg)](https://codecov.io/gh/TatraDev/pipertool)\n[![Python Version](https://img.shields.io/pypi/pyversions/pipertool.svg)](https://pypi.org/project/pipertool/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\nPiper is an open-source platform for data science and machine learning prototyping.\n\n\n## Features\n\n- Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0561/)\n- Add yours!\n\n\n## Installation\n\n```bash\npip install pipertool\n```\n\n\n## Example\n\nShowcase how your project can be used:\n\n```python\nfrom pipertool.example import some_function\n\nprint(some_function(3, 4))\n# => 7\n```\n\n## License\n\n[Apache](https://github.com/TatraDev/pipertool/blob/master/LICENSE)\n\n\n## Credits\n\nThis project was generated with [`wemake-python-package`](https://github.com/wemake-services/wemake-python-package). Current template version is: [e2cd84edbe59fa23e7c97cd448b324f3744b10ac](https://github.com/wemake-services/wemake-python-package/tree/e2cd84edbe59fa23e7c97cd448b324f3744b10ac). See what is [updated](https://github.com/wemake-services/wemake-python-package/compare/e2cd84edbe59fa23e7c97cd448b324f3744b10ac...master) since then.\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TatraDev/pipertool/tree/pipertool_pypi',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
