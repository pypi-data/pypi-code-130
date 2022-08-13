from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

li = ["javad", "kaser", "kasem", "raddi", "GPL3", "GPLv3", "GPLv3.0_only", "GPLv3.0_and_next"]

# search in li for a string with whoosh
schema = Schema(title=TEXT(stored=True))
ix = create_in("indexdir", schema)

writer = ix.writer()
for item in li:
    writer.add_document(title=item)    
writer.commit()

with ix.searcher(score = sco/) as searcher:
    query = QueryParser("title", ix.schema).parse("GPLve3")
    results = searcher.search(query)
    print(results.top_n)