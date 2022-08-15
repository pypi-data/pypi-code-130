# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['human_readable']

package_data = \
{'': ['*'],
 'human_readable': ['locale/de_DE/LC_MESSAGES/human_readable.mo',
                    'locale/en_ABBR/LC_MESSAGES/human_readable.mo',
                    'locale/es_ES/LC_MESSAGES/human_readable.mo',
                    'locale/fa_IR/LC_MESSAGES/human_readable.mo',
                    'locale/fi_FI/LC_MESSAGES/human_readable.mo',
                    'locale/fr_FR/LC_MESSAGES/human_readable.mo',
                    'locale/id_ID/LC_MESSAGES/human_readable.mo',
                    'locale/it_IT/LC_MESSAGES/human_readable.mo',
                    'locale/ja_JP/LC_MESSAGES/human_readable.mo',
                    'locale/ko_KR/LC_MESSAGES/human_readable.mo',
                    'locale/nl_NL/LC_MESSAGES/human_readable.mo',
                    'locale/pl_PL/LC_MESSAGES/human_readable.mo',
                    'locale/pt_BR/LC_MESSAGES/human_readable.mo',
                    'locale/pt_PT/LC_MESSAGES/human_readable.mo',
                    'locale/ru_RU/LC_MESSAGES/human_readable.mo',
                    'locale/sk_SK/LC_MESSAGES/human_readable.mo',
                    'locale/tr_TR/LC_MESSAGES/human_readable.mo',
                    'locale/uk_UA/LC_MESSAGES/human_readable.mo',
                    'locale/vi_VI/LC_MESSAGES/human_readable.mo',
                    'locale/zh_CN/LC_MESSAGES/human_readable.mo',
                    'locale/zh_TW/LC_MESSAGES/human_readable.mo']}

setup_kwargs = {
    'name': 'human-readable',
    'version': '1.2.2',
    'description': 'Human Readable',
    'long_description': '# Human Readable\n\n[![PyPI](https://img.shields.io/pypi/v/human-readable.svg)][pypi status]\n[![Status](https://img.shields.io/pypi/status/human-readable.svg)][pypi status]\n[![Python Version](https://img.shields.io/pypi/pyversions/human-readable)][pypi status]\n[![License](https://img.shields.io/pypi/l/human-readable)][license]\n\n[![Read the documentation at https://human-readable.readthedocs.io/](https://img.shields.io/readthedocs/human-readable/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/staticdev/human-readable/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/staticdev/human-readable/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi status]: https://pypi.org/project/human-readable/\n[read the docs]: https://human-readable.readthedocs.io/\n[tests]: https://github.com/staticdev/human-readable/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/staticdev/human-readable\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n\n## Features\n\n- File size humanization.\n\n- List humanization.\n\n- Numbers humanization.\n\n- Time and dates humanization.\n\n- Internacionalization (i18n) to 20+ locales:\n\n  - Abbreviated English (en_ABBR)\n  - Brazilian Portuguese (pt_BR)\n  - Dutch (nl_NL)\n  - Finnish (fi_FI)\n  - French (fr_FR)\n  - German (de_DE)\n  - Indonesian (id_ID)\n  - Italian (it_IT)\n  - Japanese (ja_JP)\n  - Korean (ko_KR)\n  - Persian (fa_IR)\n  - Polish (pl_PL)\n  - Portugal Portuguese (pt_PT)\n  - Russian (ru_RU)\n  - Simplified Chinese (zh_CN)\n  - Slovak (sk_SK)\n  - Spanish (es_ES)\n  - Taiwan Chinese (zh_TW)\n  - Turkish (tr_TR)\n  - Ukrainian (uk_UA)\n  - Vietnamese (vi_VI)\n\n## Requirements\n\n- It works in Python 3.7+.\n\n## Installation\n\nYou can install _Human Readable_ via [pip] from [PyPI]:\n\n```console\n$ pip install human-readable\n```\n\n<!-- basic-usage -->\n\n## Basic usage\n\nImport the lib with:\n\n```python\nimport human_readable\n```\n\nDate and time humanization examples:\n\n```python\nhuman_readable.time_of_day(17)\n"afternoon"\n\nimport datetime as dt\nhuman_readable.timing(dt.time(6, 59, 0))\n"one minute to seven hours"\n\nhuman_readable.timing(dt.time(21, 0, 40), formal=False)\n"nine in the evening"\n\nhuman_readable.time_delta(dt.timedelta(days=65))\n"2 months"\n\nhuman_readable.date_time(dt.datetime.now() - dt.timedelta(minutes=2))\n"2 minutes ago"\n\nhuman_readable.day(dt.date.today() - dt.timedelta(days=1))\n"yesterday"\n\nhuman_readable.date(dt.date(2019, 7, 2))\n"Jul 02 2019"\n\nhuman_readable.year(dt.date.today() + dt.timedelta(days=365))\n"next year"\n```\n\nPrecise time delta examples:\n\n```python\nimport datetime as dt\ndelta = dt.timedelta(seconds=3633, days=2, microseconds=123000)\nhuman_readable.precise_delta(delta)\n"2 days, 1 hour and 33.12 seconds"\n\nhuman_readable.precise_delta(delta, minimum_unit="microseconds")\n"2 days, 1 hour, 33 seconds and 123 milliseconds"\n\nhuman_readable.precise_delta(delta, suppress=["days"], format="0.4f")\n"49 hours and 33.1230 seconds"\n```\n\nFile size humanization examples:\n\n```python\nhuman_readable.file_size(1000000)\n"1.0 MB"\n\nhuman_readable.file_size(1000000, binary=True)\n"976.6 KiB"\n\nhuman_readable.file_size(1000000, gnu=True)\n"976.6K"\n```\n\nLists humanization examples:\n\n```python\nhuman_readable.listing(["Alpha", "Bravo"], ",")\n"Alpha, Bravo"\n\nhuman_readable.listing(["Alpha", "Bravo", "Charlie"], ";", "or")\n"Alpha; Bravo or Charlie"\n```\n\nNumbers humanization examples:\n\n```python\nhuman_readable.int_comma(12345)\n"12,345"\n\nhuman_readable.int_word(123455913)\n"123.5 million"\n\nhuman_readable.int_word(12345591313)\n"12.3 billion"\n\nhuman_readable.ap_number(4)\n"four"\n\nhuman_readable.ap_number(41)\n"41"\n```\n\nFloating point number humanization examples:\n\n```python\nhuman_readable.fractional(1.5)\n"1 1/2"\n\nhuman_readable.fractional(0.3)\n"3/10"\n```\n\nScientific notation examples:\n\n```python\nhuman_readable.scientific_notation(1000)\n"1.00 x 10³"\n\nhuman_readable.scientific_notation(5781651000, precision=4)\n"5.7817 x 10⁹"\n```\n\n<!-- end-basic-usage -->\n\nComplete instructions can be found at [human-readable.readthedocs.io].\n\n## Localization\n\nHow to change locale at runtime:\n\n```python\nimport datetime as dt\nhuman_readable.date_time(dt.timedelta(seconds=3))\n\'3 seconds ago\'\n\n_t = human_readable.i18n.activate("ru_RU")\nhuman_readable.date_time(dt.timedelta(seconds=3))\n\'3 секунды назад\'\n\nhuman_readable.i18n.deactivate()\nhuman_readable.date_time(dt.timedelta(seconds=3))\n\'3 seconds ago\'\n```\n\nYou can pass additional parameter `path` to `activate` to specify a path to search\nlocales in.\n\n```python\nhuman_readable.i18n.activate("xx_XX")\n...\nFileNotFoundError: [Errno 2] No translation file found for domain: \'human_readable\'\nhuman_readable.i18n.activate("pt_BR", path="path/to/my/portuguese/translation/")\n<gettext.GNUTranslations instance ...>\n```\n\nYou can see how to add a new locale on the [Contributor Guide].\n\nA special locale, `en_ABBR`, renderes abbreviated versions of output:\n\n```python\nhuman_readable.date_time(datetime.timedelta(seconds=3))\n3 seconds ago\n\nhuman_readable.int_word(12345591313)\n12.3 billion\n\nhuman_readable.date_time(datetime.timedelta(seconds=86400*476))\n1 year, 3 months ago\n\nhuman_readable.i18n.activate(\'en_ABBR\')\nhuman_readable.date_time(datetime.timedelta(seconds=3))\n3s\n\nhuman_readable.int_word(12345591313)\n12.3 B\n\nhuman_readable.date_time(datetime.timedelta(seconds=86400*476))\n1y 3M\n```\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT] license,\n_Human Readable_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis lib is based on original [humanize] with some added features such as listing, improved naming, documentation, functional tests, type-annotations, bug fixes and better localization.\n\nThis project was generated from [@cjolowicz]\'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/staticdev/human-readable/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[contributor guide]: https://github.com/staticdev/human-readable/blob/main/CONTRIBUTING.md\n[cookiecutter]: https://github.com/audreyr/cookiecutter\n[human-readable.readthedocs.io]: https://human-readable.readthedocs.io\n[humanize]: https://github.com/jmoiron/humanize\n[mit]: http://opensource.org/licenses/MIT\n',
    'author': 'staticdev',
    'author_email': 'staticdev-support@proton.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/staticdev/human-readable',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
