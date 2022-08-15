# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiopywttr']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8,<4.0', 'pywttr-models>=1.0,<2.0']

setup_kwargs = {
    'name': 'aiopywttr',
    'version': '2.0.1',
    'description': 'Asynchronous wrapper for wttr.in API',
    'long_description': '# aiopywttr\n\n[![CI](https://github.com/monosans/aiopywttr/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/monosans/aiopywttr/actions/workflows/ci.yml)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/monosans/aiopywttr/main.svg)](https://results.pre-commit.ci/latest/github/monosans/aiopywttr/main)\n[![codecov](https://codecov.io/gh/monosans/aiopywttr/branch/main/graph/badge.svg)](https://codecov.io/gh/monosans/aiopywttr)\n\nAsynchronous wrapper for [wttr.in](https://wttr.in) weather forecast API.\n\nSynchronous version [here](https://github.com/monosans/pywttr).\n\n## Installation\n\n```bash\npython -m pip install aiopywttr\n```\n\n## Example\n\nThis example prints the average temperature in New York today.\n\n```python\nimport asyncio\n\nfrom aiopywttr import Wttr\n\n\nasync def main():\n    wttr = Wttr("New York")\n    forecast = await wttr.en()\n    print(forecast.weather[0].avgtemp_c)\n\n\nasyncio.run(main())\n```\n\nOther languages may also be used instead of `en`. For a complete list of supported languages, follow the code completion in your IDE.\n\n## Documentation\n\nThere is no documentation, just follow the code completion in your IDE.\n\nFor an example of type annotations, see `pywttr-models` [README.md](https://github.com/monosans/pywttr-models#usage-for-type-annotation).\n\n## Recommended IDEs\n\n- [Visual Studio Code](https://code.visualstudio.com) (with [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))\n- [PyCharm](https://jetbrains.com/pycharm)\n\n## License\n\n[MIT](https://github.com/monosans/aiopywttr/blob/main/LICENSE)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/aiopywttr',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
