# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['oastodcat']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'datacatalogtordf>=2.1.2,<3.0.0',
 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'oastodcat',
    'version': '2.0.2',
    'description': 'A library for transforming an openAPI file to one or more dcat:DataService',
    'long_description': '# oastodcat\n\n![Tests](https://github.com/Informasjonsforvaltning/oastodcat/workflows/Tests/badge.svg)\n[![codecov](https://codecov.io/gh/Informasjonsforvaltning/oastodcat/branch/master/graph/badge.svg)](https://codecov.io/gh/Informasjonsforvaltning/oastodcat)\n[![PyPI](https://img.shields.io/pypi/v/oastodcat.svg)](https://pypi.org/project/oastodcat/)\n[![Read the Docs](https://readthedocs.org/projects/oastodcat/badge/)](https://oastodcat.readthedocs.io/)\n\nA small Python library to transform an openAPI file to a dcat:DataService\n\nAt this moment we support all 3.0.x versions of [The OpenAPI specification](https://github.com/OAI/OpenAPI-Specification)\n\n## Usage\n\n### Install\n\n```Shell\n% pip install oastodcat\n```\n\n### Getting started\n\nExample usage:\n\n```Shell\nimport yaml\nimport requests\nfrom datacatalogtordf import Catalog\nfrom oastodcat import OASDataService\n\n# Create catalog object\ncatalog = Catalog()\ncatalog.identifier = "http://example.com/catalogs/1"\ncatalog.title = {"en": "A dataset catalog"}\ncatalog.publisher = "https://example.com/publishers/1"\n\n# Create a dataservice based on an openAPI-specification:\nurl = ("https://raw.githubusercontent.com/"\n      "OAI/OpenAPI-Specification/master/examples/v3.0/petstore.yaml"\n     )\noas = yaml.safe_load(requests.get(url).text)\nidentifier = "http://example.com/dataservices/{id}"\noas_spec = OASDataService(url, oas, identifier)\n#\n# Add dataservices to catalog:\nfor dataservice in oas_spec.dataservices:\n  catalog.services.append(dataservice)\n\nget dcat representation in turtle (default)\ndcat = catalog.to_rdf()\n# Get dcat representation in turtle (default)\ndcat = catalog.to_rdf()\nprint(dcat)\n```\n\n## Mapping\n\nThe following table shows how an openAPI specification is mapped to a dcat:DataService:  \n(Only dcat:DataService properties are shown.)\n\n| dcat:DataService         | RDF property             | openAPI v 3.0.x      | Note |\n|--------------------------|--------------------------|----------------------|------|\n| endpoint description     | dcat:endpointDescription | _url to description_ |      |\n| endpoint URL             | dcat:endpointURL         | servers.url          | [1]  |\n| serves dataset           |                          | _n/a_                |      |\n| access rights            |                          |                      |      |\n| conforms to              | dct:conformsTo           |                      |      |\n| contact point            | dcat:contactPoint        | info.contact         |      |\n| creator                  |                          |                      |      |\n| description              | dct:description          | info.description     |      |\n| has policy               |                          |                      |      |\n| identifier               |                          | _n/a_                |      |\n| is referenced by         |                          |                      |      |\n| keyword/tag              |                          |                      |      |\n| landing page             | dcat:landingPage         | externalDocs         |      |\n| license                  | dct:license              | info.license.url     |      |\n| resource language        |                          |                      |      |\n| relation                 |                          |                      |      |\n| rights                   |                          |                      |      |\n| qualified relation       |                          |                      |      |\n| publisher                | dct:publisher            |                      |      |\n| release date             |                          |                      |      |\n| theme/category           |                          |                      |      |\n| title                    | dct:title                | info.title           |      |\n| type/genre               |                          |                      |      |\n| update/modification date |                          |                      |      |\n| qualified attribution    |                          |                      |      |\n| _media type_             | dcat:mediaType           | <it\'s complicated>   |      |\n\n[1] For each url in the servers object array, an instance of dcat:DataService will be created.\n\n## Development\n\n### Requirements\n\n- python3\n- [pyenv](https://github.com/pyenv/pyenv) (recommended)\n- [pipx](https://github.com/pipxproject/pipx) (recommended)\n- [poetry](https://python-poetry.org/)\n- [nox](https://nox.thea.codes/en/stable/)\n- [nox-poetry](https://pypi.org/project/nox-poetry/)\n\n```Shell\n% pipx install poetry==1.0.5\n% pipx install nox==2019.11.9\n% pipx inject nox nox-poetry\n```\n\n### Install dependencies\n\n```Shell\n\n```Shell\n% git clone https://github.com/Informasjonsforvaltning/oastodcat.git\n% cd oastodcat\n% pyenv install 3.8.6\n% pyenv install 3.9.0\n% pyenv install 3.10.4\n% poetry install\n```\n\n### Run all sessions\n\n```Shell\n% nox\n```\n\n### Run all tests with coverage reporting\n\n```Shell\n% nox -rs tests\n```\n\n### Debugging\n\nYou can enter into [Pdb](https://docs.python.org/3/library/pdb.html) by passing `--pdb` to pytest:\n\n```Shell\nnox -rs tests -- --pdb\n```\n\nYou can set breakpoints directly in code by using the function `breakpoint()`.\n',
    'author': 'Stig B. Dørmænen',
    'author_email': 'stigbd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Informasjonsforvaltning/oastodcat',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
