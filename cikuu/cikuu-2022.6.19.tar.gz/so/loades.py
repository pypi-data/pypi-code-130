# 2022.8.15 , cp from esjson_load.py 
import json,fire,sys, os, hashlib ,time , requests, fileinput
from collections import Counter , defaultdict
from elasticsearch import Elasticsearch,helpers
import so 

def esjson_load(infile, idxname:str=None, batch=1000000, refresh:bool=True, eshost='127.0.0.1',esport=9200): 
	''' python3 -m so.loades gzjc.esjson.gz '''
	es	  = Elasticsearch([ f"http://{eshost}:{esport}" ])  
	if not idxname : idxname = infile.split('.')[0]
	print(">>started: " , infile, idxname, flush=True )
	if refresh: 
		if es.indices.exists(index=idxname):es.indices.delete(index=idxname)
		es.indices.create(index=idxname, body=so.config) #, body=snt_mapping

	actions=[]
	for line in fileinput.input(infile,openhook=fileinput.hook_compressed): 
		try:
			arr = json.loads(line.strip())
			actions.append( {'_op_type':'index', '_index':idxname, '_id': arr.get('_id',None), '_source': arr.get('_source',{}) } )
			if len(actions) >= batch: 
				helpers.bulk(client=es,actions=actions, raise_on_error=False)
				print ( actions[-1], flush=True)
				actions = []
		except Exception as e:
			print("ex:", e)	
	if actions : helpers.bulk(client=es,actions=actions, raise_on_error=False)
	print(">>finished " , infile, idxname )

if __name__ == '__main__':
	fire.Fire(esjson_load)

'''
{"_index": "gzjc", "_type": "_doc", "_id": "2897-stype", "_source": {"src": 2897, "tag": "simple_snt", "type": "stype"}}
import warnings
warnings.filterwarnings("ignore")
'''