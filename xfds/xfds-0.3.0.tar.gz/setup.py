# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['xfds']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'Markdown>=3.3.6,<4.0.0',
 'Pint>=0.19.2,<0.20.0',
 'PyYAML>=6.0,<7.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['xfds = xfds.cli:app']}

setup_kwargs = {
    'name': 'xfds',
    'version': '0.3.0',
    'description': 'Utility for managing FDS models',
    'long_description': '\n\n![Last Commit](https://img.shields.io/github/last-commit/pbdtools/xfds)\n[![Tests](https://github.com/pbdtools/xfds/workflows/Tests/badge.svg)](https://github.com/pbdtools/xfds/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/pbdtools/xfds/main/graph/badge.svg)](https://codecov.io/gh/pbdtools/xfds)\n\n![Python](https://img.shields.io/pypi/pyversions/xfds.svg)\n![Implementation](https://img.shields.io/pypi/implementation/xfds)\n![License](https://img.shields.io/github/license/pbdtools/xfds.svg)\n\n[![PyPI](https://img.shields.io/pypi/v/xfds.svg)](https://pypi.org/project/xfds)\n![Development Status](https://img.shields.io/pypi/status/xfds)\n![Wheel](https://img.shields.io/pypi/format/xfds)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/xfds)\n\nSource Code: [github.com/pbdtools/xfds](https://github.com/pbdtools/xfds)\n\nDocumentation: [xfds.pbd.tools](https://xfds.pbd.tools)\n\n\n![xFDS Logo](https://raw.githubusercontent.com/pbdtools/xfds/main/docs/assets/xfds_logo_lg.png)\n\nDo you have FDS installed on your machine? Do you know where the FDS executable is located? Do you know what version it is? If you installed FDS and Pathfinder, you might have multiple versions of FDS on your machine, but which one do you use?\n\nxFDS leverages the power of Docker to give you acess to all the versions of FDS without having to manage the different versions of FDS yourself. Best of all, you don\'t have to change or install anything when FDS has a new release!\n\nOnce xFDS is installed, all you have to do is navigate to your file and type `xfds run`. It will locate the first FDS file in the directory and run it with the latest version of FDS!\n\n```\n~/tests/data/fds$ ls\ntest.fds\n~/tests/data/fds$ xfds run\ndocker run --rm --name test -v /tests/data/fds:/workdir openbcl/fds fds test.fds\n```\n\n## Features\n\n### Generate Parametric Analyses\n\nFire models can often require mesh sensitivity studies, different fire sizes, multiple exhaust rates, and a number of differnt parameters. With the power of the [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) templating system, xFDS can help generate a variety of models from a single `.fds` file!\n\n**Specify Resolution, not `IJK`**\n\nLet xFDS calculate the number of cells so you don\'t have to. By setting variables at the top of your FDS file, you can use them to perform calculations. Variables are defined using the [MultiMarkdown Specification](https://fletcherpenney.net/multimarkdown/#metadata) for file metadata. Expressions between curly braces `{` and `}` are evaluated as Python code.\n\n```\nxmax: 5\nymax: 4\nzmax: 3\nres: 0.1\n\n&MESH XB=0, {xmax}, 0, {ymax}, 0, {zmax}, IJK={xmax // res}, {ymax // res}, {zmax // res}/\n```\n\nWill translate to:\n\n```\n&MESH XB= 0, 5, 0, 4, 0, 3, IJK= 50, 40, 30/\n```\n\nWant to run a coarser mesh? Just change `res` to `0.2` and get\n\n```\n&MESH XB= 0, 5, 0, 4, 0, 3, IJK= 25, 20, 15/\n```\n\n**Use loops to create an array of devices**\n\nCreate [for loops](https://jinja.palletsprojects.com/en/3.1.x/templates/#for) by typing `{% for item in list %} ... {% endfor %}`.\n\n```\n{% for x in range(1, 5) %}\n{% for y in range(1, 3) %}\n&DEVC QUANTITY=\'TEMPERATURE\', IJK={x}, {y}, 1.8/\n{% endfor %}\n{% endfor %}\n```\n\nWill render to the following code. Note, [Python\'s `range()`](https://docs.python.org/3.3/library/stdtypes.html?highlight=range#range) function will exclude the upper bound.\n\n```\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=1, 1, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=1, 2, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=2, 1, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=2, 2, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=3, 1, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=3, 2, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=4, 1, 1.8/\n&DEVC QUANTITY=\'TEMPERATURE\', IJK=4, 2, 1.8/\n```\n\n\n### Manage FDS Runs\n\n**Auto-detect FDS file in directory**\n\nIf you\'re in a directory containing an FDS file, xFDS will find the FDS file without you specifying it. This is best when each FDS model has its own directory. If multiple FDS files are in the directory, only the first file found will be executed.\n\nIf no FDS file is found, xFDS will put you into an interactive session with the directory mounted inside the Docker container. If no directory is specified, the current working directory will be used.\n\n**Latest version of FDS always available.**\n\nxFDS will always default to the latest version thanks to how the Docker images are created, but you\'re always welcome to use an older version of FDS if needed. See [fds-dockerfiles](https://github.com/openbcl/fds-dockerfiles) for supported versions.\n\n**Always know what FDS version you\'re using.**\n\nxFDS will inject the FDS version into the container name so there\'s no question what version of FDS is running. xFDS will also append a globally unique ID so there\'s no conflicts in having multipe containers running.\n\n**Runs in Background**\n\nFire and forget. Unless you use the interactive mode, xFDS will run your model in a container and free up the terminal for you to keep working.\n\n## Installation\n\n### Prerequisites\nxFDS depends on the following softwares:\n\n- [Docker](https://www.docker.com/): Needed to run fds-dockerfiles images\n- [Python](https://www.python.org/): Needed to run pipx\n- [pipx](https://pypa.github.io/pipx/): Needed to install xFDS\n\nOnce Docker, Python, and pipx are installed, install xFDS with the following command:\n\n```\npipx install xfds\n```\n\nFor more information about installing xFDS, see https://xfds.pbd.tools/installation\n\n\n<a href="https://xfds.pbd.tools" style="font-size: 2em; text-align: center; padding: 1em; border: 1px solid #444; display: block; color: rgb(255, 110, 66);">\nLearn more at xfds.pbd.tools\n</a>\n',
    'author': 'Brian Cohan',
    'author_email': 'briancohan@pbd.tools',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://xfds.pbd.tools',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
