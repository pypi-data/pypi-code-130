#2022.8.18  https://segmentfault.com/a/1190000017825534 # 2022.2.9 https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_2_TAGGING.md
from uvirun import *

@app.get('/flair/frame/snt')
def frame_snt(snt:str="He had a look at different hats."):    
	''' He had <have.LV> a look <look.01> at different hats .   https://github.com/flairNLP/flair/blob/master/resources/docs/TUTORIAL_2_TAGGING.md '''
	from flair.data import Sentence
	from flair.models import SequenceTagger
	if not hasattr(frame_snt, 'tagger'):  frame_snt.tagger = SequenceTagger.load('frame-fast')  # 115M 
	sentence_1 = Sentence(snt)
	frame_snt.tagger.predict(sentence_1)
	return sentence_1.to_tagged_string()

@app.post('/flair/frame/snts')
def frame_snts(snts:list=["George returned to Berlin to return his hat.","He had a look at different hats."]):  
	''' ["George returned to Berlin to return his hat.","He had a look at different hats."]	'''
	return { snt: frame_snt(snt) for snt in snts }

if __name__ == '__main__': 
	print (frame_snt())

@app.get('/flair/sentiment')
def classify_sentiment(snt:str="He had a look at different hats."): 
	''' 2022.2.18 '''
	from flair.models import TextClassifier
	from flair.data import Sentence
	if not hasattr(classify_sentiment, 'sentiment'): 
		classify_sentiment.sentiment = TextClassifier.load("sentiment-fast") 
	sentence = Sentence(snt)
	classify_sentiment.sentiment.predict(sentence)
	return sentence.labels[0] 

@app.post('/flair/sentiment/snts')
def classify_sentiment_snts(snts:list=["He had a look at different hats.","I am too tired to move on."]): 
	''' ["He had a look at different hats.","I am too tired to move on."] '''
	return { snt: classify_sentiment(snt) for snt in snts}

'''
https://www.geeksforgeeks.org/flair-a-framework-for-nlp/#:~:text=The%20Flair%20Embedding%20is%20based%20on%20the%20concept,better%20results.%20Flair%20supports%20a%20number%20of%20languages.
[
  {
    "_value": "sci",
    "_score": 0.9978132247924805
  }
]
2022-02-19 20:14:21,967 loading file /models/flair-sci-twit.pt
2022-02-19 20:14:28,579 loading file /home/ubuntu/.flair/models/sentiment-en-mix-ft-rnn_v8.pt

>>> s.get_spans()
[<have.03-span (2): "had">, <look.01-span (4): "look">]

# iterate and print
for entity in s.get_spans('ner'):
    print(entity)

>>> spans[0].text
'had'
>>> spans[0].tag
'have.03'
>>> spans[0].to_dict()
{'text': 'had', 'start_pos': 3, 'end_pos': 6, 'labels': [have.03 (0.8889)]}

>>> spans[0].labels[0].to_dict()
{'value': 'have.03', 'confidence': 0.8889056444168091}
>>> spans[0].labels[0].value
'have.03'
'''