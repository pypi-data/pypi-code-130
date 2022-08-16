# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pygismeteo']

package_data = \
{'': ['*']}

install_requires = \
['pygismeteo-base>=3.0,<4.0', 'requests>=2.28,<3.0']

setup_kwargs = {
    'name': 'pygismeteo',
    'version': '5.0.2',
    'description': 'Wrapper for Gismeteo API',
    'long_description': '# pygismeteo\n\n[![CI](https://github.com/monosans/pygismeteo/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/monosans/pygismeteo/actions/workflows/ci.yml)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/monosans/pygismeteo/main.svg)](https://results.pre-commit.ci/latest/github/monosans/pygismeteo/main)\n[![codecov](https://codecov.io/gh/monosans/pygismeteo/branch/main/graph/badge.svg)](https://codecov.io/gh/monosans/pygismeteo)\n\nОбёртка для [Gismeteo API](https://gismeteo.ru/api/).\n\nАсинхронная версия [здесь](https://github.com/monosans/aiopygismeteo).\n\n## Установка\n\n```bash\npython -m pip install -U pygismeteo\n```\n\n## Документация\n\n[pygismeteo.readthedocs.io](https://pygismeteo.readthedocs.io/)\n\n## Пример, выводящий температуру в Москве сейчас\n\n```python\nfrom pygismeteo import Gismeteo\n\ngismeteo = Gismeteo()\nsearch_results = gismeteo.search.by_query("Москва")\ncity_id = search_results[0].id\ncurrent = gismeteo.current.by_id(city_id)\nprint(current.temperature.air.c)\n```\n\n## License / Лицензия\n\n[MIT](https://github.com/monosans/pygismeteo/blob/main/LICENSE)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/pygismeteo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
