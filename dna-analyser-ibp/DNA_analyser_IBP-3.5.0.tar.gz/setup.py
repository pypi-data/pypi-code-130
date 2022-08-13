# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['DNA_analyser_IBP',
 'DNA_analyser_IBP.adapters',
 'DNA_analyser_IBP.interfaces',
 'DNA_analyser_IBP.intersection',
 'DNA_analyser_IBP.models',
 'DNA_analyser_IBP.ports']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib==3.0.3',
 'pandas==1.0.0',
 'pyjwt==1.7.1',
 'requests-toolbelt==0.9.1',
 'requests==2.20.0',
 'tenacity==6.1.0',
 'tqdm==4.28']

setup_kwargs = {
    'name': 'dna-analyser-ibp',
    'version': '3.5.0',
    'description': 'DNA analyser API wrapper tool for Jupiter notebooks.',
    'long_description': '<h1 align=\'center\'> DNA analyser IBP </h1>\n<br />\n<div align="center">\n    <a href="https://pypi.org/project/dna-analyser-ibp/">\n    <img src="https://img.shields.io/badge/Version 3.5.0-green?style=for-the-badge" alt=\'package_version\'/>\n    </a>\n    <img src="https://img.shields.io/badge/Python 3.6+-00599C?style=for-the-badge&logo=python&logoColor=white" alt=\'python_version\'/>\n    <img src="https://img.shields.io/badge/jupyter-gray?style=for-the-badge&logo=jupyter" alt=\'jupyter\'/>\n    <a href="https://choosealicense.com/licenses/gpl-3.0/">\n            <img src="https://img.shields.io/badge/gnu-white?style=for-the-badge&logo=gnu&logoColor=black" alt=\'licence\'/>\n    </a>\n</div>\n<br />\n\nTool for creating R-loop tracker, P53predictor, G4Killer and G4Hunter analysis. Work as API wrapper for IBP DNA analyzer API [bioinformatics.ibp](http://bioinformatics.ibp.cz/).\nCurrently working with an instance of DNA analyser server running on http://bioinformatics.ibp.cz computational core but can be switched \nto the local instance of the server.\n\n# Getting Started\n\n## Prerequisites\n\npython >= 3.6\n\n## Installing\n\nTo install test version from [Pypi](https://pypi.org/project/dna-analyser-ibp/).\n\n```commandline\npipenv install dna-analyser-ibp\n```\n\n```commandline\npip install dna-analyser-ibp\n```\n\n## Documentation\n\nMethods are documented in the following [documentation](https://patrikkaura.gitlab.io/DNA_analyser_IBP/).\n\n## Quick start\n\nDNA analyser uses `pandas.Dataframe` or `pandas.Series`. Firstly the user  has to create `Api` object and login to API.\n```python\nfrom DNA_analyser_IBP.api import Api\n\nAPI = Api()\n```\n```python\nEnter your email        example@example.cz\nEnter your password     ········\n\n2020-09-16 18:51:17.943398 [INFO]: User host is trying to login ...\n2020-09-16 18:51:17.990580 [INFO]: User host is successfully loged in ...\n```\nIf DNA analyser API server is not running on http://bioinformatics.ibp.cz then you have to set server paramether to create `Api` object.\n```python\nfrom DNA_analyser_IBP.api import Api\n\nAPI = Api(\n    server=\'http://hostname:port/api\'\n)\n```\n\n## Sequence uploading\nSequences can be uploaded from NCBI, plain text or text file. Example bellow illustrates NCBI sequence uploading `Homo sapiens chromosome 12`.\n```python\nAPI.sequence.ncbi_creator(\n    circular= True,\n    tags=[\'Homo\',\'sapiens\', \'chromosome\'],\n    name=\'Homo sapiens chromosome 12\',\n    ncbi_id=\'NC_000012.12\'\n)\n\nAPI.sequence.load_all(\n    tags=[\'Homo\']\n)\n```\n\n## G4Hunter\nG4Hunter is a tool for prediction of G-quadruplex propensity in nucleic acids, this algorithm considers G-richness and G-skewness of a tested sequence and shows a quadruplex propensity score. \n```python\nsapiens = API.g4hunter.load_all(\n    tags=[\'Homo\']\n)\n\nAPI.g4hunter.analyse_creator(\n    sequence=sapiens,\n    tags=[\'analyse\',\'Homo\', \'sapiens\'],\n    threshold=1.4,\n    window_size=30\n)\n```\nTo load results of G4Hunter analysis.\n```python\nAPI.g4hunter.load_all(\n    tags=[\'analyse\', \'Homo\', \'sapiens\']\n) \n```\n\n## R-loop tracker\n R-loop tracker is a toll for prediction of R-loops in nucleic acids. The algorithms search for R-loop initiation zone based on presence of G-clusters and R-loop elongation zone containing at least 40% of Guanine density.\n```python\nsapiens = API.g4hunter.load_all(\n    tags=[\'Homo\']\n)\nAPI.rloopr.analyse_creator(\n    sequence=sapiens,\n    tags=[\'analyse\', \'Homo\', \'sapiens\'],\n    riz_2g_cluster=True,\n    riz_3g_cluster=False\n)\n```\nTo load results of R-loop tracker analysis.\n```python\nAPI.rloopr.load_all(\n    tags=[\'analyse\', \'Homo\', \'sapiens\']\n) \n```\n\n## G4Killer\nG4Killer algorithm allows to mutate DNA sequences with desired G4Hunter score with minimal mutation steps.\n```python\nAPI.g4killer.run(\n    sequence=\'AATTATTTGGAAAGGGGGGGTTTTCCGA\',\n    threshold=0.5\n) \n\nAPI.g4killer.run_multiple(\n    sequences=[\n        \'AATTATTTGGAAAGGGGGGGTTTTCCGA\',\n        \'AATTATTTGGAAAGGGGGGGTTTTCCGA\'\n    ],\n    threshold=0.5\n)\n```\n## P53 predictor\nP53 binding predictor for 20 base pairs sequences. \n```python\nAPI.p53.run(\n    sequence=\'GGACATGCCCGGGCATGTCC\'\n)\n\nAPI.p53.run_multiple(\n    sequences=[\n        \'GGACATGCCCGGGCATGTCC\',\n        \'GGACATGCCCGGGCATGTCC\'\n    ]\n) \n```\n\n# Development\n\n## Dependencies\n\n* tenacity >= 6.1.0\n* requests >= 2.20\n* requests-toolbelt >= 0.9.1\n* pyjwt >= 1.7.1\n* pandas >= 0.23\n* matplotlib >= 3.0.3\n* tqdm >= 4.28\n\n## DEV dependencies\n\n* pytest = "^6.0.2"\n* black = "^20.0"\n\n## Tests\n\nTo run tests only when downloaded directly from this repository.\n\n```commandline\npytest -v tests/\n```\n\n## Authors\n\n* **Patrik Kaura** - *Main developer* - [patrikkaura](https://gitlab.com/PatrikKaura/)\n* **Jan Kolomaznik** - *Supervisor* - [jankolomaznik](https://github.com/Kolomaznik)\n* **Jiří Šťastný** - *Supervisor*\n\n## License\n\nThis project is licensed under the GPL-3.0 License - see the [LICENSE.md](LICENSE.md) file for details.\n',
    'author': 'Patrik Kaura',
    'author_email': 'patrikkaura@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://bioinformatics.ibp.cz/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.6.15',
}


setup(**setup_kwargs)
