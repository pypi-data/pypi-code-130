from .entrez_search_accids import entrez_search_accids


def entrez_download_accids(**kwargs):
    term = kwargs.get('term', 'cas15')
    filename = kwargs.get('filename', f'{term}.list')
    record = entrez_search_accids(**kwargs)
    res = '\n'.join(record['IdList'])

    open(filename, "w").write(res)
