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
    'version': '0.3.0',
    'description': 'Simple library to make your Indonesian NLP project easier.',
    'long_description': '# indoNLP\n\n[![PyPI version](https://badge.fury.io/py/indoNLP.svg)](https://badge.fury.io/py/indoNLP)\n[![Python Version](https://img.shields.io/badge/python-≥3.7-blue?logo=python)](https://python.org)\n[![Test](https://github.com/Hyuto/indo-nlp/actions/workflows/testing.yaml/badge.svg)](https://github.com/Hyuto/indo-nlp/actions/workflows/testing.yaml)\n[![Lint](https://github.com/Hyuto/indo-nlp/actions/workflows/linting.yaml/badge.svg)](https://github.com/Hyuto/indo-nlp/actions/workflows/linting.yaml)\n[![codecov](https://codecov.io/gh/Hyuto/indo-nlp/branch/master/graph/badge.svg?token=094QNPJ3X4)](https://codecov.io/gh/Hyuto/indo-nlp)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n---\n\nBahasa | [English](https://github.com/Hyuto/indo-nlp/blob/master/README.en.md)\n\nindoNLP adalah library python sederhana yang bertujuan untuk memudahkan proyek NLP anda.\n\n## Installation\n\nindoNLP dapat diinstall dengan mudah dengan menggunakan `pip`:\n\n```bash\n$ pip install indoNLP\n```\n\n## Preprocessing\n\nModul `indoNLP.preprocessing` menyediakan beberapa fungsi umum untuk menyiapkan dan melakukan\ntransformasi terhadap data teks mentah untuk digunakan pada konteks tertentu.\n\n**Generics**\n\n1. `remove_html`\n\n   Menghapus html tag yang terdapat di dalam teks\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_html\n   >>> remove_html("website <a href=\'https://google.com\'>google</a>")\n   "website google"\n   ```\n\n2. `remove_url`\n\n   Menghapus url yang terdapat di dalam teks\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_url\n   >>> remove_url("retrieved from https://gist.github.com/gruber/8891611")\n   "retrieved from"\n   ```\n\n3. `remove_stopwords`\n\n   > Stopwords merupakan kata yang diabaikan dalam pemrosesan dan biasanya disimpan di dalam stop lists. Stop list ini berisi daftar kata umum yang mempunyai fungsi tapi tidak mempunyai arti\n\n   Menghapus stopwords yang terdapat di dalam teks.\n   List stopwords bahasa Indonesia didapatkan dari https://stopwords.net/indonesian-id/\n\n   ```python\n   >>> from indoNLP.preprocessing import remove_stopwords\n   >>> remove_stopwords("siapa yang suruh makan?!!")\n   "suruh makan?!!"\n   ```\n\n4. `replace_slang`\n\n   Mengganti kata gaul (_slang_) menjadi kata formal tanpa mengubah makna dari kata tersebut.\n   List kata gaul (_slang words_) bahasa Indonesian didapatkan dari\n   [Kamus Alay - Colloquial Indonesian Lexicon](https://github.com/nasalsabila/kamus-alay)\n   oleh Salsabila, Ali, Yosef, and Ade\n\n   ```python\n   >>> from indoNLP.preprocessing import replace_slang\n   >>> replace_slang("emg siapa yg nanya?")\n   "memang siapa yang bertanya?"\n   ```\n\n5. `replace_word_elongation`\n\n   > Word elongation adalah tindakan untuk menambahkan huruf ke kata, biasanya di akhir kata\n\n   Meghandle word elongation\n\n   ```python\n   >>> from indoNLP.preprocessing import replace_word_elongation\n   >>> replace_word_elongation("kenapaaa?")\n   "kenapa?"\n   ```\n\n**Emoji**\n\nPreproses teks yang mengandung emoji.\n\n1. `emoji_to_words`\n\n   Mengubah emoji yang berada dalam sebuah teks menjadi kata - kata yang sesuai dengan emoji\n   tersebut.\n\n   ```python\n   >>> from indoNLP.preprocessing import emoji_to_words\n   >>> emoji_to_words("emoji 😀😁")\n   "emoji !wajah_gembira!!wajah_gembira_dengan_mata_bahagia!"\n   ```\n\n2. `words_to_emoji`\n\n   Mengubah kata - kata dengan kode emoji menjadi emoji.\n\n   ```python\n   >>> from indoNLP.preprocessing import words_to_emoji\n   >>> words_to_emoji("emoji !wajah_gembira!")\n   "emoji 😀"\n   ```\n\n**Pipelining**\n\nMembuat pipeline dari sequance fungsi preprocessing\n\n```python\n>>> from indoNLP.preprocessing import pipeline, replace_word_elongation, replace_slang\n>>> pipe = pipeline([replace_word_elongation, replace_slang])\n>>> pipe("Knp emg gk mw makan kenapaaa???")\n"kenapa memang enggak mau makan kenapa???"\n```\n\n## Development\n\nSetup local dev environment.\n\n```bash\nmake setup-dev\n```\n',
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
