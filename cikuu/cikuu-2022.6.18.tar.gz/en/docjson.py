# 2022.8.14 , depend on spacy3.4.1 lg model 
import json, traceback,sys, time,  fileinput, os #https://docs.python.org/3/library/fileinput.html
import spacy 
from spacy.tokens import Doc
nlp =spacy.load(f'en_core_web_lg')
spacy.nlp = nlp 
simple_sent		= lambda doc:  len([t for t in doc if t.pos_ == 'VERB' and t.dep_ != 'ROOT']) <= 0 # else is complex sent 
compound_snt	= lambda doc:  len([t for t in doc if t.dep_ == 'conj' and t.head.dep_ == 'ROOT']) > 0

import terms,verbnet
attach = lambda doc: ( terms.lempos_type(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

def train(infile, outfile=None, model:str="lg", key:str="doc_txt"):
	''' spider.docjson => spider.jsonlg.3.4.1 , 2022.8.2'''
	import spacy 
	nlp =spacy.load(f'en_core_web_{model}')
	if outfile is None: outfile = infile.split('.')[0] + f".docjson{model}." + spacy.__version__
	print ("started:", infile ,  ' -> ',  outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for line in fileinput.input(infile,openhook=fileinput.hook_compressed): #for line in fileinput.input(infile):
			try:
				arr = json.loads(line.strip())
				essay = arr.get(key, '')
				if not essay: continue 
				doc = nlp(essay) 
				res = doc.to_json() 
				res['info'] = arr 
				fw.write( json.dumps(res) + "\n")
			except Exception as e:
				print ("ex:", e, line) 
	os.system(f"gzip -f -9 {outfile}")
	print ("finished:", infile, outfile ) 

def sntdoc_idsour(sid, snt, doc): 
	''' 2022.6.18 '''
	actions = []
	actions.append( {'_id': sid, '_source': 
		{'type':'snt', 'snt':snt,  'src': sid,  'tc': len(doc),  #'pred_offset': en.pred_offset(doc),
		'kp': [ f"{t.lemma_}:{t.pos_}" for t in doc if t.pos_ not in ('PUNCT')] + [ f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}" for t in doc if t.pos_ not in ('PUNCT')],  #added 2022.6.23 | "select snt from gzjc where type = 'snt' and kp = 'book_VERB' limit 2"
		'postag':"_^ " + ' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in doc]),
		} } )
	[ actions.append( {'_id': f"{sid}-tok-{t.i}", '_source': 
		{"type":"tok", "src":sid, 'i':t.i, "head":t.head.i, 'lex':t.text, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gpos":t.head.pos_, "glem":t.head.lemma_, "gov":t.head.lemma_ + "_" + t.head.pos_ } }) for t in doc ] # "gov" is verbose , to be removed later  | "trp": f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}",
	[ actions.append( {'_id': f"{sid}-np-{sp.start}", '_source': 
		{"type":"np", "src":sid,  'lempos':doc[sp.end-1].lemma_  + "_" + doc[sp.end-1].pos_, 'chunk':sp.text.lower(), 'start':sp.start, 'end':sp.end} }) for sp in doc.noun_chunks ]
	[ actions.append( {'_id': f"{sid}-{id}", '_source': dict(sour, **{"src":sid}) } ) for id, sour in attach(doc).items() if not id.startswith('tok-') and not id.startswith('trp-')]
	actions.append( { '_id': f"{sid}-stype", '_source': {"type":"stype", "tag": "simple_snt" if simple_sent(doc) else "complex_snt", "src":sid} } )
	if compound_snt(doc) : actions.append( { '_id': f"{sid}-stype-compound", '_source': {"type":"stype", "tag": "compound_snt", "src":sid} } )
	return actions

def snt_esjson(infile,  model:str="lg",):
	''' gzjc.docjsonlg.3.4.1.gz -> gzjc.esjson '''
	outfile = infile.split('.')[0] + f".esjson"
	start = time.time()
	print ("started:", infile ,  ' -> ',  outfile, flush=True)
	with open(outfile, 'w') as fw: 
		for sid, line in enumerate(fileinput.input(infile,openhook=fileinput.hook_compressed)): 
			try:
				arr = json.loads(line.strip())
				doc = Doc(nlp.vocab).from_json(arr)				#res['info'] = {"tm": arr.get("timestamp",""), "url":arr.get('url','')}
				for ar in sntdoc_idsour(sid, doc.text, doc):
					fw.write(json.dumps(ar) + "\n") 
			except Exception as e:
				print ("ex:", e, sid, line) 
	os.system(f"gzip -f -9 {outfile}")
	print(f"{infile} is finished, \t| using: ", time.time() - start) 

if __name__	== '__main__':
	import fire 
	fire.Fire()

'''
>>> doc.to_json()
{'text': 'I am a boy.', 'ents': [], 'sents': [{'start': 0, 'end': 11}], 'tokens': [{'id': 0, 'start': 0, 'end': 1, 'tag': 'PRP', 'pos': 'PRON', 'morph': 'Case=Nom|Number=Sing|Person=1|PronType=Prs', 'lemma': 'I', 'dep': 'nsubj', 'head': 1}, {'id': 1, 'start': 2, 'end': 4, 'tag': 'VBP', 'pos': 'AUX', 'morph': 'Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin', 'lemma': 'be', 'dep': 'ROOT', 'head': 1}, {'id': 2, 'start': 5, 'end': 6, 'tag': 'DT', 'pos': 'DET', 'morph': 'Definite=Ind|PronType=Art', 'lemma': 'a', 'dep': 'det', 'head': 3}, {'id': 3, 'start': 7, 'end': 10, 'tag': 'NN', 'pos': 'NOUN', 'morph': 'Number=Sing', 'lemma': 'boy', 'dep': 'attr', 'head': 1}, {'id': 4, 'start': 10, 'end': 11, 'tag': '.', 'pos': 'PUNCT', 'morph': 'PunctType=Peri', 'lemma': '.', 'dep': 'punct', 'head': 1}]}

 [{'id': 0,
   'start': 0,
   'end': 3,
   'tag': 'PRP',
   'pos': 'PRON',
   'morph': 'Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs',
   'lemma': 'she',
   'dep': 'nsubj',
   'head': 1},
'''