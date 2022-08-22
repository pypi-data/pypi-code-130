from Bio import Entrez


def entrez_search_accids(**kwargs):
    limit = kwargs.get('limit', 100)
    term = kwargs.get('term', 'cas15')
    db = kwargs.get('db', 'protein')

    Entrez.email = "A.N.Other@example.com"  # Always tell NCBI who you are
    handle = Entrez.esearch(db=db, term=term, retmax=limit)
    return Entrez.read(handle)