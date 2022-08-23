# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastlid']

package_data = \
{'': ['*']}

install_requires = \
['fasttext>=0.9.2,<0.10.0', 'logzero>=1.7.0,<2.0.0', 'numpy>=1.20.3,<2.0.0']

setup_kwargs = {
    'name': 'fastlid',
    'version': '0.1.8',
    'description': 'Detect languages via a fasttext model',
    'long_description': '# fastlid\n<!--- repo_name  pack_name  mod_name func_name --->\n[![tests](https://github.com/ffreemt/fast-langid/actions/workflows/routine-tests.yml/badge.svg)][![python](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/fastlid.svg)](https://badge.fury.io/py/fastlid)\n\nLanguage identification based on fasttext (lid.176.ftz https://fasttext.cc/docs/en/language-identification.html).\n\nThe `lid.176.ftz` file is licensed under  Creative Commons Attribution-Share-Alike License 3.0 and is not part of this module. It is automatically downloaded from its external origin on the first run of this module.\n\nThis module attempts to immitate the follow two features of `langid`\n*   langid.classify: fastlid\n*   langid.set_languages(langs=[...]): fastlid.set_languages = [...]\n    *   import fastlid\n    *   fastlid.set_languages = [\'nl\',\'fr\'])\n*   TODO: Commandline interface\n\n## Preinstall fasttext for Windows without C compiler\n\nFor Windows without a C/C++ compiler:\n* Download a proper whl (e.g., `fasttext‑0.9.2‑cp36‑cp36m‑win_amd64.whl` for 64bits Python 3.6 etc)  from [https://www.lfd.uci.edu/~gohlke/pythonlibs/#fasttext](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fasttext)\n```bash\npip install fasttext*.whl\n```\n\nThis step is not needed if a C/C++ compiler (e.g. Visual C) is present in the system.\n\n## Install it\n\n```bash\npip install fastlid\n```\nor install from `git`\n```bash\npip install git+https://github.com/ffreemt/fast-langid.git\n\n# also works pip install git+https://github.com/ffreemt/fast-langid\n```\nor clone the git repo and install from source.\n\n## Use it\n```python\nfrom fastlid import fastlid, supported_langs\n\n# support 176 languages\nprint(supported_langs, len(supported_langs))\n# [\'af\', \'als\', \'am\', \'an\', \'ar\', \'arz\', \'as\', \'ast\', \'av\', \'az\'] 176\n\nfastlid("test this")\n# (\'en\', 0.765)\n\nfastlid("test this 测试一下", k=2)\n# ([\'zh\', \'en\'], [0.663, 0.124])\n\nfastlid.set_languages = [\'fr\', \'zh\']\nfastlid("test this 测试吧")\n# (\'zh\', 0.01)\n\nfastlid.set_languages = None\nfastlid("test this 测试吧")\n(\'en\', 0.686)\n\nfastlid.set_languages = [\'fr\', \'zh\', \'en\']\nfastlid("test this 测试吧", k=3)\n([\'en\', \'zh\', \'fr\'], [0.686, 0.01, 0.006])\n```\n\nN.B. `hanzidentifier` can be used to identify simplified Chinese or/and traditional Chinese should you need to do so.\n\n## For Developers\nInstall `poetry` and `yarn` the way you like it.\n```bash\npoetry install  # install python packages\nyarn install --dev  # install necesary node packages\n\n# ...code...\nyarn test\nyarn final\n\n# ...optionally submit pr...\n```',
    'author': 'freemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/fast-langid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
