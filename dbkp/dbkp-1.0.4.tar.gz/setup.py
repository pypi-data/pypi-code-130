# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbkp']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['dbkp = dbkp.dbkp:main']}

setup_kwargs = {
    'name': 'dbkp',
    'version': '1.0.4',
    'description': 'Dotfiles backup and restore tool',
    'long_description': '# dbkp - dotfiles backup\n\ndbkp simply backups and restores dotfiles using `rsync -La`. You can use it with\nany version control or backup strategy you want.\n\n## Instalation\n\nInstall with pip:\n\n`pip3 install dbkp`\n\n## Usage\n\nPut the file dbkp.json on a folder and configure it as you want. Then either run\n`dbkp backup` from the folder or pass the path to the configuration file as\n`dbkp backup /path/to/dbkp.json`. A folder named dotfiles in the same folder as\nthe configuration file will be created and all dotfiles will be synced inside\nit. Use `dbkp restore` in the same way to rsync the files from the dotfiles\nfolder into their places.\n\n## Configuration example\n\nThe configuration is a list of files to backup, or objects that adds some\nfeatures to the specific dotfile.\n\nA string will backup the folder/file. This will backup the file `~/.vimrc`:\n\n```json\n["~/.vimrc"]\n```\n\nIt is the same as\n\n```json\n[\n  {\n    "path": "~/.vimrc",\n    "alias": "vimrc"\n  }\n]\n```\n\n`alias` is the name the file/folder will have inside the dotfiles folder. By\ndefault it is the name of the file/folder without a leading dot.\n\nIt is also possible to exclude subfiles/subfolders from a folder. The complete\nfolder will be synced and then the files/folders will be deleted. You can\nspecify both `only` and `exclude`, but `exclude` will be ignored in this case.\n`only` will remove all files but the ones listed and `exclude` will only exclude\nthe ones listed.\n\n```json\n[\n  {\n    "path": "~/.config/fish",\n    "only": ["functions"],\n    "exclude": ["completions"]\n  }\n]\n```\n\nThe `links` options allows to create symlinks after restoring. It is a list of\neither strings or lists of 2 string elements. If the element is a string, then a\nsymlink will be created pointing to `path`. If it a list of 2 strings, the\nsecond is the symlink and will point to `path`/`first element`. In the example,\n`~/.vimrc` will point to `~/.config/nvim/init.nvim` and `~/neovim` will point to\n`~/.config/nvim`.\n\n```json\n[\n  {\n    "path": "~/.config/nvim",\n    "links": ["~/neovim", ["init.vim", "~/.vimrc"]]\n  }\n]\n```\n\nIt is also possible to run commands to do the backup/restore.\n\n```json\n[\n  {\n    "backup": "brew leaves",\n    "restore": "xargs brew install",\n    "alias": "brew.leaves"\n  }\n]\n```\n\nThis is the same as backing up with\n\n```sh\nbrew leaves > brew.leaves\n```\n\nand then restoring with\n\n```sh\ncat brew.leaves | xargs brew install\n```\n\nThe current working directory is changed to the folder containing the\nconfiguration file before executing anything, so if you want to specify files in\nthe command line, remember that: you need to quote file paths if they contain\nspaces and your `alias` file is in `dotfiles/:alias"`.\n\n## LICENSE\n\nThe MIT License (MIT)\n\nCopyright (c) 2021 Álan Crístoffer e Sousa\n\nPermission is hereby granted, free of charge, to any person obtaining\na copy of this software and associated documentation files (the\n"Software"), to deal in the Software without restriction, including\nwithout limitation the rights to use, copy, modify, merge, publish,\ndistribute, sublicense, and/or sell copies of the Software, and to\npermit persons to whom the Software is furnished to do so, subject to\nthe following conditions:\n\nThe above copyright notice and this permission notice shall be\nincluded in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\nEXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.\nIN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY\nCLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,\nTORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\nSOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
    'author': 'Álan Crístoffer',
    'author_email': 'acristoffers@startmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/acristoffers/dbkp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
