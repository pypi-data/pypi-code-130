from Bio import Entrez


def entrez_download_accids(**kwargs):
    limit = kwargs.get('limit', 100)
    term = kwargs.get('term', 'cas15')
    db = kwargs.get('db', 'protein')
    filename = kwargs.get('filename', f'{term}.list')

    Entrez.email = "A.N.Other@example.com"  # Always tell NCBI who you are
    handle = Entrez.esearch(db=db, term=term, retmax=limit)
    record = Entrez.read(handle)

    open(filename, "w").write(record['IdList'])
