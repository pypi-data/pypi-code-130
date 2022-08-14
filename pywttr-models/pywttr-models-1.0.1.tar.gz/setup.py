# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pywttr_models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9,<2.0']

setup_kwargs = {
    'name': 'pywttr-models',
    'version': '1.0.1',
    'description': 'Pydantic models for pywttr and aiopywttr',
    'long_description': '# pywttr-models\n\n[![CI](https://github.com/monosans/pywttr-models/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/monosans/pywttr-models/actions/workflows/ci.yml)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/monosans/pywttr-models/main.svg)](https://results.pre-commit.ci/latest/github/monosans/pywttr-models/main)\n\n[Pydantic](https://github.com/samuelcolvin/pydantic) models for [pywttr](https://github.com/monosans/pywttr) and [aiopywttr](https://github.com/monosans/aiopywttr).\n\n## Usage for type annotation\n\n```python\nimport pywttr_models\n\n\ndef do_something(model: pywttr_models.en.Model):\n    ...\n```\n\nOther languages may also be used instead of `en`. For a complete list of supported languages, follow the code completion in your IDE.\n\n## License\n\n[MIT](https://github.com/monosans/pywttr-models/blob/main/LICENSE)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/pywttr-models',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
