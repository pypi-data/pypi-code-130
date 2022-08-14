# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['repo_autoindex', 'repo_autoindex._impl']

package_data = \
{'': ['*'], 'repo_autoindex._impl': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2', 'aiohttp>=3.8.1', 'defusedxml>=0.7.1']

entry_points = \
{'console_scripts': ['repo-autoindex = repo_autoindex._impl.cmd:entrypoint']}

setup_kwargs = {
    'name': 'repo-autoindex',
    'version': '1.0.1',
    'description': 'Generic static HTML indexes of various repository types',
    'long_description': "# repo-autoindex\n\nGenerate static HTML indexes of various repository types\n\n![Build Status](https://github.com/release-engineering/repo-autoindex/actions/workflows/ci.yml/badge.svg?branch=main)\n![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)\n[![Docs](https://img.shields.io/website?label=docs&url=https%3A%2F%2Frelease-engineering.github.io%2Frepo-autoindex%2F)](https://release-engineering.github.io/repo-autoindex/)\n[![PyPI](https://img.shields.io/pypi/v/repo-autoindex)](https://pypi.org/project/repo-autoindex/)\n\n## Overview\n\n`repo-autoindex` provides a minimal CLI and Python library to generate static HTML indexes\nfor certain types of content, such as yum repositories.\n\n```\npip install repo-autoindex\nREPO_URL=$(curl -s 'https://mirrors.fedoraproject.org/mirrorlist?repo=updates-released-f36&arch=x86_64' | egrep '^http' | head -n1)\nrepo-autoindex $REPO_URL\nxdg-open index.html\n```\n\nSee [the manual](https://release-engineering.github.io/repo-autoindex/) for more\ninformation about the usage of `repo-autoindex`.\n\n## Changelog\n\n### v1.0.1 - 2022-08-15\n\n- Use correct SPDX license identifier in package metadata.\n\n### v1.0.0 - 2022-08-15\n\n- Initial stable release.\n\n## License\n\nThis program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.\n",
    'author': 'Rohan McGovern',
    'author_email': 'rmcgover@redhat.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/release-engineering/repo-autoindex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
