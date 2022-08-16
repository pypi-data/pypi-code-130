SOURCE_URL = 'https://kbbi.co.id'
WORD_DETAIL_URL = f'{SOURCE_URL}/arti-kata'
WORD_LIST_URL = f'{SOURCE_URL}/daftar-kata'
WORD_SEARCH_URL = f'{SOURCE_URL}/cari?kata='

SYMBOL = {
    'a': {
        'verbose': 'Adjektiva',
        'meaning': 'Bentuk Kata Sifat'
    },
    'v': {
        'verbose': 'Verba',
        'meaning': 'Bentuk Kata Kerja'
    },
    'n': {
        'verbose': 'Nomina',
        'meaning': 'Bentuk Kata Benda'
    },
    'ki': {
        'verbose': 'Kiasan',
        'meaning': 'Bentuk Kata Kiasan'
    },
    'pron': {
        'verbose': 'Pronomina',
        'meaning': 'Bentuk Kata Yang Meliputi Kata Ganti, Kata Tunjuk, Atau Kata Tanya'
    },
    'cak': {
        'verbose': None,
        'meaning': 'Bentuk Kata Percakapan (Tidak Baku)'
    },
    'ark': {
        'verbose': 'Arkais',
        'meaning': 'Bentuk Kata Yang Tidak Lazim Digunakan'
    },
    'adv': {
        'verbose': 'Adverbia',
        'meaning': 'Bentuk Kata Yang Berupa Kata Keterangan'
    }
}