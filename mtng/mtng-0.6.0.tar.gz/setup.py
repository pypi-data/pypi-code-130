# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mtng']

package_data = \
{'': ['*'], 'mtng': ['template/*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'gidgethub>=5.0.1,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pytest-asyncio>=0.19.0,<0.20.0',
 'pytest-dotenv>=0.5.2,<0.6.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'python-dotenv>=0.17.1,<0.18.0',
 'requests>=2.25.1,<3.0.0',
 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['mtng = mtng.cli:cli']}

setup_kwargs = {
    'name': 'mtng',
    'version': '0.6.0',
    'description': '',
    'long_description': '# mtng \nGenerate meeting notes from GitHub + [Indico](https://getindico.io/). This tool generates\nLaTeX code that can be compiled into a PDF presentation. The result looks something like this:\n\n![Screenshot of the tool\'s output](screen.png)\n\n## Installation\n\n```console\npip install mtng\n```\n\n## Interface\n\n```console\n$ mtng --help\nUsage: mtng [OPTIONS] COMMAND [ARGS]...\n\n  Meeting generation script, version 0.4.1\n\nOptions:\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n  --help                          Show this message and exit.\n\nCommands:\n  generate  Generate a LaTeX fragment that includes an overview of PRs,...\n  preamble  Print a preamble suitable to render fancy output\n  schema    Print the configuration schema\n\n```\n\n```console\n$ mtng generate --help\nUsage: mtng generate [OPTIONS] CONFIG\n\n  Generate a LaTeX fragment that includes an overview of PRs, Issues and\n  optionally an Indico agenda\n\nArguments:\n  CONFIG  [required]\n\nOptions:\n  --token TEXT                    Github API token to use. Can be supplied\n                                  with environment variable GH_TOKEN\n  --since [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]\n                                  Start window for queries  [required]\n  --now [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]\n                                  End window for queries  [default:\n                                  2022-08-17T21:24:07]\n  --event TEXT                    Optionally attach an Indico based agenda\n                                  overview. This only works with public\n                                  events!\n  --full                          Write a full LaTeX file that is compileable\n                                  on it\'s own\n  --pdf FILE                      Compile the report as a PDF file. This\n                                  requires a LaTeX installation.\n  --help                          Show this message and exit.\n\n```\n\n## Configuration\n\n`mtng` consumes a configuration file to specify which GitHub repositories to ingest. An example configuration could look like this:\n\n```yml\nrepos:\n  - name: acts-project/acts\n    stale_label: Stale\n    wip_label: ":construction: WIP"\n    show_wip: true\n    do_recent_issues: true\n    no_assignee_attention: true\n    filter_labels: \n      - backport\n```\n\n### Schema \n- **`Repository`** *(object)*: Cannot contain additional properties.\n  - **`name`** *(string)*: Name of the repository, e.g. \'acts-project/acts\'.\n  - **`wip_label`** *(string)*: Label to identify WIP PRs.\n  - **`show_wip`** *(boolean)*: If true, WIP PRs will be included in the output, else they are ignored. Default: `False`.\n  - **`filter_labels`** *(array)*: If any PR or issue has any label that matches any of these labels, they are excluded.\n    - **Items** *(string)*\n  - **`stale_label`** *(string)*: A label to identify stale PRs/issues. If set, stale PRs and issues will be listed separately and split into newly and other stale items.\n  - **`do_open_prs`** *(boolean)*: Show a list of open PRs. Default: `True`.\n  - **`do_merged_prs`** *(boolean)*: Show a list of merged PRs. Default: `True`.\n  - **`do_recent_issues`** *(boolean)*: Show a list of issues opened in the time interval. Default: `False`.\n  - **`no_assignee_attention`** *(boolean)*: Draw attention to items without an assignee. Default: `True`.\n- **`Spec`** *(object)*: Cannot contain additional properties.\n  - **`repos`** *(array)*\n    - **Items**: Refer to *#/definitions/Repository*.\n\nThis configuration will look up the `acts-project/acts` repository. The output will contain sections on \n\n1. Stale PRs and issues. If this is turned on, the `stale_label` key must be given as well\n2. A list of open PRs, optionally filtered to not include the label given by `wip_label`\n3. Merged PRs since the date given by the `--since` option\n4. Issues opened since the date given by the `--since` option\n\n\nIn addition and independent of this config, a meeting agenda can be attached at the end if the `--event` option is provided and contains a valid Indico URL.\n\n## Making a presentation\n\nBy default, the output of `mtng generate` is a LaTeX fragment. It has to be incorporated into a set of Beamer/LaTeX slides, for example like\n\n```console\n$ mtng generate spec.yml > gen.tex\n```\n\nwith a LaTeX file like\n\n```latex\n% Preamble and beginnig of slides\n\\input{gen.tex}\n% Rest of slides\n```\n\nAlternatively, you can generate a fully compileable LaTex document, by using the `--full` option.\n\n```console\n$ mtng generate spec.yml --full > gen.tex\n$ latexmk gen.tex\n```\n',
    'author': 'Paul Gessinger',
    'author_email': 'hello@paulgessinger.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
