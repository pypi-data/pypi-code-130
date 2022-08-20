# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pard']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pard',
    'version': '0.1.2',
    'description': '',
    'long_description': "## PARD (Physicochemical Amino acid Replacement Distances)\n\n\n### Overview\nAmino acid replacements (also referred to as substitutions) are changes from one amino acid to a different one in a\nprotein - and there are different ways to assess the difference between the two amino acids that come into play in an\namino acid replacement.\n\nOne can look at one or several properties' discrepancy between two amino acids. To list only a few: polarity [1][3][4],\nmolecular volume / relative sizes of amino-acid side chains [1][3][4], mean number of lone pair electrons on the \nside-chain [2], maximum moment of inertia for rotation at the α―β bond [2] or at the β―γ bond [2] or at the γ―δ\nbond [2], presence of a pyrrolidine ring (proline (P)) [2], experimental protein activity and stability after \nexchanging one amino acid into another [5], etc.\n\n`pard` is a package designed to make those **P**hysicochemical **A**mino acid **R**eplacement **D**istances calculations\nstraightforward with Python.\n\nOne typical use is to establish a 'distance' between a wild-type protein and its mutated version.\n\n\n### Getting started\n#### Install from PyPI (recommended)\nTo use `pard`, run `pip install pard` in your terminal.\n\n#### Usage\n\n\n#### Unit tests\n```\nName                              Stmts   Miss  Cover\n\n-----------------------------------------------------\npard\\__init__.py                      2      0   100%\npard\\grantham.py                      4      0   100%\npard\\raw_python_dictionaries.py      18     10    44%\ntests\\__init__.py                     0      0   100%\ntests\\test_grantham.py               15      0   100%\ntests\\test_pard.py                    3      0   100%\n-----------------------------------------------------\nTOTAL                                42     10    76%\n```\n\n\n### About the source code\n- Follows [PEP8](https://peps.python.org/pep-0008/) Style Guidelines.\n- All variables are correctly type-hinted, reviewed with [static type checker](https://mypy.readthedocs.io/en/stable/)\n`mypy`.\n\n\n### Useful links:\n- [Corresponding GitHub repository](https://github.com/MICS-Lab/pard)\n- [Corresponding PyPI page](https://pypi.org/project/pard/)\n\n\n### References\n- [1] Grantham, R., 1974. Amino acid difference formula to help explain protein evolution. science, 185(4154), \npp.862-864.\n- [2] Sneath, P.H.A., 1966. Relations between chemical structure and biological activity in peptides. Journal of\ntheoretical biology, 12(2), pp.157-195.\n- [3] Epstein, C.J., 1967. Non-randomness of ammo-acid changes in the evolution of homologous proteins. Nature,\n215(5099), pp.355-359.\n- [4] Miyata, T., Miyazawa, S. and Yasunaga, T., 1979. Two types of amino acid substitutions in protein evolution. \nJournal of molecular evolution, 12(3), pp.219-236.\n- [5] Yampolsky, L.Y. and Stoltzfus, A., 2005. The exchangeability of amino acids in proteins. Genetics, 170(4), \npp.1459-1472.\n",
    'author': 'JasonMendoza2008',
    'author_email': 'lhotteromain@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
