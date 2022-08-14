# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ingresso']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'ingresso',
    'version': '0.1.2',
    'description': 'A wrapper python para o ingresso.com',
    'long_description': '# Ingresso.com\n\nUm wrapper em python para o ingresso.com\n\n[![Python package](https://github.com/hudsonbrendon/ingresso.com/actions/workflows/python-package.yml/badge.svg)](https://github.com/hudsonbrendon/ingresso.com/actions/workflows/python-package.yml)\n[![Github Issues](http://img.shields.io/github/issues/hudsonbrendon/ingresso.com.svg?style=flat)](https://github.com/hudsonbrendon/ingresso.com/issues?sort=updated&state=open)\n![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)\n\n\n![Logo](https://www.exibidor.com.br/fotos/noticias/notundefined_1544192395.png)\n\n# Recursos Disponíveis\n\n- [x] Cinemas de uma cidade\n\n- [x] Sessões de um cinema\n\n- [x] Filmes em destaques\n\n- [x] Filmes em cartaz\n\n- [x] Filmes que serão lançados em brevve\n\n# Instalação\n\n```bash\n$ pip install ingresso\n```\nou\n\n```bash\n$ poetry build\n```\n\n# Modo de usar\n\nPara utilizar a classe Ingresso, primeiro você precisa pegar o ID da cidade em questão, o ingresso.com disponibiliza um endpoint que lista as cidades e seus respectivos ids. Comece acessando o endpoint abaixo passando a UF do estado:\n\n[https://api-content.ingresso.com/v0/states/UF](https://api-content.ingresso.com/v0/states/UF)\n\n## Tabela de UFs:\n| UF        | Estate  |\n| --------- |:-----:|\n| AC      | Acre |\n| AL      | Alagoas |\n| AP      | Amapá |\n| AM      | Amazonas |\n| BA      | Bahia |\n| CE      | Ceará |\n| DF      | Distrito Federal |\n| ES      | Espírito Santo |\n| GO      | Goiás |\n| MT      | Mato Grosso |\n| MA      | Maranhão |\n| MS      | Mato Grosso do Sul |\n| MG      | Minas Gerais |\n| PA      | Pará |\n| PB      | Paraíba |\n| PR      | Paraná |\n| PE      | Pernambuco |\n| PI      | Piauí |\n| RJ      | Rio de Janeiro |\n| RN      | Rio Grande do Norte |\n| RS      | Rio Grande do Sul |\n| RO      | Rondônia |\n| RR      | Roraima |\n| SC      | Santa Catarina |\n| SP      | São Paulo |\n| SE      | Sergipe |\n| TO      | Tocantins |\n\n## Exemplo:\n\nhttps://api-content.ingresso.com/v0/states/RN\n\nSerá retornado algo semelhante a isso:\n\n```json\n{\n  "name": "Rio Grande do Norte",\n  "uf": "RN",\n  "cities": [\n    {\n      "id": "48",\n      "name": "Natal",\n      "uf": "RN",\n      "state": "Rio Grande do Norte",\n      "urlKey": "natal",\n      "timeZone": "America/Fortaleza"\n    }\n  ]\n}\n```\n\nNo exemplo acima, o ID da cidade é o 48, é ele que deve ser usado no parâmetro **city_id**.\n\nO parâmetro **partnership** é o nome do cinema, por exemplo: cinepolis, cinemark, knoplex, moviecom, etc.\n\n## Cinemas\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.theaters()\n```\nou \n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.theaters(1005)\n```\n\n## Cinemas por cidade\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.teathers_by_city()\n```\n\n## Sessões por cinema\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.sessions_by_theater(1005)\n```\n\n## Destaques por cinema\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.highlights()\n```\n\n## Filmes em cartaz\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.now_playing()\n```\n\n## Filmes em breve\n\n```python\ningresso = Ingresso(48, \'cinepolis\')\n\ningresso.soon()\n```\n\n# Contribua\n\nClone o projeto repositório:\n\n```bash\n$ git clone https://github.com/hudsonbrendon/ingresso.com.git\n```\n\nCertifique-se de que o [Poetry](https://python-poetry.org/) está instalado, caso contrário:\n\n```bash\n$ pip install -U poetry\n```\n\nInstale as dependências:\n\n```bash\n$ poetry install\n```\n\n```bash\n$ poetry shell\n```\n\nPara executar os testes:\n\n```bash\n$ pytest\n```\n\n# Dependências\n\n- [Python >=3.8](https://www.python.org/downloads/release/python-3813/)\n\n# Licença\n\n[MIT](http://en.wikipedia.org/wiki/MIT_License)\n',
    'author': 'Hudson Brendon',
    'author_email': 'contato.hudsonbrendon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hudsonbrendon/ingresso.com#readme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
