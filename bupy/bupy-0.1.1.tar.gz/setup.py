# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bupy']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'pyxdg>=0.28,<0.29',
 'rich>=12.5.1,<13.0.0',
 'ruamel.yaml>=0.17.21,<0.18.0',
 'typer[all]>=0.6.1,<0.7.0',
 'urllib3>=1.26.10,<2.0.0']

entry_points = \
{'console_scripts': ['bupy = bupy.cli:app']}

setup_kwargs = {
    'name': 'bupy',
    'version': '0.1.1',
    'description': 'A Python toolkit for Butane and Ignition',
    'long_description': '# Bupy\n\nThe **Bu**tane **Py**thon Toolkit\n\nBupy was built to help users develop Butane configurations for Fedora CoreOS quickly on their workstations. It allows you to convert Butane YAML to Ignition JSON and render Butane Jinja2 templates to either Butane YAML or Ignition JSON. You can then use your Butane file or template to launch a local QEMU Virtual Machine.\n\n### Requirements\n\n* [Python 3.8.10^](https://www.python.org/downloads/)\n* [butane](https://coreos.github.io/butane/)\n* [qemu](https://www.qemu.org/download/)\n* If possible, a positive attitude\n\n### Roadmap\n- [x] Convert Support\n- [x] Jinja2 Template Support\n- [x] Launch a local QEMU FCOS VM\n- [ ] Merge Butane YAML (snippets)\n- [ ] Serve Ignition JSON via HTTP\n- [ ] Libvirt support\n\n### Demo\n\nYou can watch a quick demo of Bupy on Youtube.\n\n[![Quick demo of Bupy for Fedora CoreOS](https://img.youtube.com/vi/yBOEz827TUU/0.jpg)](https://www.youtube.com/watch?v=yBOEz827TUU)\n\n### Development\n\n1) Clone this repo\n1) Install dependencies\n  ```\n  poetry install\n  ```\n1) Activate a poetry shell\n  ```\n  $ poetry shell\n  Spawning shell within /home/jdoss/src/quickvm/bupy/.venv\n  . /home/jdoss/src/quickvm/bupy/.venv/bin/activate\n  $ . /home/jdoss/src/quickvm/bupy/.venv/bin/activate\n  ```\n1) Make changes...\n1) See them in action\n  ```\n  (.venv) $ python -m bupy --help\n\n   Usage: bupy [OPTIONS] COMMAND [ARGS]...\n\n  ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮\n  │ --version             -v        Show the version and exit.                                       │\n  │ --install-completion            Install completion for the current shell.                        │\n  │ --show-completion               Show completion for the current shell, to copy it or customize   │\n  │                                 the installation.                                                │\n  │ --help                          Show this message and exit.                                      │\n  ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n  ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮\n  │ convert      Converts Butane YAML to Ignition JSON                                               │\n  │ merge        Merge Butane files together                                                         │\n  │ qemu         Launches a QEMU VM with the specified Ignition JSON or Butane YAML                  │\n  │ serve        Serve an ignition file via HTTP on a specified port                                 │\n  │ template     Render Butane Jinja2 templates                                                      │\n  ╰──────────────────────────────────────────────────────────────────────────────────────────────────╯\n  ```\n\n## License\n\n                                 Apache License\n                           Version 2.0, January 2004\n                        http://www.apache.org/licenses/\n\n                          Copyright 2022 QuickVM, LLC\n\n   Licensed under the Apache License, Version 2.0 (the "License");\n   you may not use this file except in compliance with the License.\n   You may obtain a copy of the License at\n\n       http://www.apache.org/licenses/LICENSE-2.0\n\n   Unless required by applicable law or agreed to in writing, software\n   distributed under the License is distributed on an "AS IS" BASIS,\n   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n   See the License for the specific language governing permissions and\n   limitations under the License.\n',
    'author': 'QuickVM',
    'author_email': 'hello@quickvm.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.10,<4.0.0',
}


setup(**setup_kwargs)
