# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['formatting', 'labels', 'names']

package_data = \
{'': ['*']}

install_requires = \
['pybtex>=0.24.0,<0.25.0']

entry_points = \
{'pybtex.style.formatting': ['apa7 = formatting.apa:APAStyle'],
 'pybtex.style.labels': ['apa7 = labels.apa:LabelStyle'],
 'pybtex.style.names': ['firstlast = names.firstlast:NameStyle']}

setup_kwargs = {
    'name': 'pybtex-apa7-style',
    'version': '0.1.1',
    'description': 'Provides APA7 style for Pybtex',
    'long_description': '# APA7 Style for Pybtex\n\n*This is a fork of [naeka\'s pybtex-apa-style](https://github.com/naeka/pybtex-apa-style)*.\n\n[Pybtex](https://pybtex.org/) provides Python support for interacting with bibtex-formatted\nbibliography information. Style plugins are required to format a bibliography in a given \nstyle, similar to the role that `csl` files play for LaTeX.\n\nThis plugin provides APA7 style.\n\n## Installation\n\n```\n$ pip install pybtex pybtex-apa7-style\n```\n\n## Usage\n\nPybtex uses [Python\'s plugin system](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/).\nTo use APA7, load it as a plugin.\n\n```\nfrom pybtex.plugin import find_plugin\nfrom pybtex.database import parse_file\nAPA = find_plugin(\'pybtex.style.formatting\', \'apa7\')()\nHTML = find_plugin(\'pybtex.backends\', \'html\')()\n\ndef bib_to_apa7_html(bibfile):\n    bibliography = parse_file(bibfile, \'bibtex\')\n    formatted_bib = APA.format_bibliography(bibliography)\n    return "<br>".join(entry.text.render(HTML) for entry in formatted_bib)\n```\n',
    'author': 'Chris Proctor',
    'author_email': 'github.com@accounts.chrisproctor.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cproctor/pybtex-apa7-style',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
