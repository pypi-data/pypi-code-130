# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['indoNLP',
 'indoNLP.dataset',
 'indoNLP.preprocessing',
 'indoNLP.preprocessing.emoji']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'indonlp',
    'version': '0.3.1',
    'description': 'Simple python library with zero additional dependencies to make your Indonesian NLP project easier.',
    'long_description': '# indoNLP\n\n[![PyPI version](https://badge.fury.io/py/indoNLP.svg)](https://badge.fury.io/py/indoNLP)\n[![Python Version](https://img.shields.io/badge/python-≥3.7-blue?logo=python)](https://python.org)\n[![Test](https://github.com/Hyuto/indo-nlp/actions/workflows/testing.yaml/badge.svg)](https://github.com/Hyuto/indo-nlp/actions/workflows/testing.yaml)\n[![Lint](https://github.com/Hyuto/indo-nlp/actions/workflows/linting.yaml/badge.svg)](https://github.com/Hyuto/indo-nlp/actions/workflows/linting.yaml)\n[![codecov](https://codecov.io/gh/Hyuto/indo-nlp/branch/master/graph/badge.svg?token=094QNPJ3X4)](https://codecov.io/gh/Hyuto/indo-nlp)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n---\n\nBahasa | [English](https://github.com/Hyuto/indo-nlp/blob/master/README.en.md)\n\nindoNLP adalah library python sederhana tanpa dependency tambahan yang bertujuan untuk memudahkan proyek NLP anda.\n\n## Installasi\n\nindoNLP dapat diinstall dengan mudah dengan menggunakan `pip`:\n\n```bash\n$ pip install indoNLP\n```\n\n## Quick Start\n\n**Mengakses Indonesian NLP Open Dataset**\n\nMengakses Indonesian NLP Open Dataset dengan cepat dan mudah.\n\n```python\nfrom indoNLP.dataset import Dataset\n\nhandler = Dataset("id-multi-label-hate-speech-and-abusive-language-detection")\ndata = handler.read()\n```\n\nJika data bersifat simetrik maka data dapat ditabelisasi menggunakan `pandas.DataFrame`\n\n```python\nimport pandas as pd\n\ndf = pd.DataFrame(data)\n```\n\n**Preprocessing Data Teks**\n\nMenerjemahkan emoji dan mengganti kata gaul (_slang words_)\n\n```python\nfrom indoNLP.preprocessing import emoji_to_words, replace_slang, pipeline\n\npipe = pipeline([emoji_to_words, replace_slang])\npipe("library yg membara 🔥")\n# "library yang membara !api!"\n```\n\n## Development\n\nSetup local dev environment. `indoNLP` menggunakan [python-poetry](https://python-poetry.org/)\nuntuk packaging dan management dependencies.\n\n```bash\n$ make setup-dev\n```\n',
    'author': 'Wahyu Setianto',
    'author_email': 'wahyusetianto19@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
