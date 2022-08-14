import spacy
from spacy import displacy
from spacy import pipeline
from spacy.language import Language
from spacy.tokens import Doc, Token, Span
from spacy.pipeline import Sentencizer

import dadmatools.models.normalizer as normalizer
import dadmatools.models.tokenizer as tokenizer
import dadmatools.models.mw_tokenizer as mwt
import dadmatools.models.lemmatizer as lemmatizer


class NLP():
    """
    In this class a blank pipeline in created and it is initialized based on our trained models
    possible pipelines: [tokenizer, lemmatize, postagger, dependancyparser]
    """
    tokenizer_model = None
    mwt_model = None
    lemma_model = None
    postagger_model = None
    depparser_model = None
    consparser_model = None
    chunker_model = None
    normalizer_model = None
    ner_model = None
    kasreh_model = None
    
    Token.set_extension("dep_arc", default=None)
    Doc.set_extension("sentences", default=None)
    Doc.set_extension("chunks", default=None)
    Doc.set_extension("constituency", default=None)
    Doc.set_extension("ners", default=None)
    Doc.set_extension("kasreh_ezafe", default=None)
    
    global nlp
    nlp = None
    
    def __init__(self, lang, pipelines):
        
        global nlp
        nlp = spacy.blank(lang)
        self.nlp = nlp
        
        self.dict = {'tok':'tokenizer', 'lem':'lemmatize'}
        self.pipelines = pipelines.split(',')

        global tokenizer_model
        tokenizer_model = tokenizer.load_model()
        self.nlp.add_pipe('tokenizer')
        
        global mwt_model
        mwt_model = mwt.load_model()

        if 'lem' in pipelines:
            global lemma_model
            lemma_model = lemmatizer.load_model()
            self.nlp.add_pipe('lemmatize')
        

    @Language.component('tokenizer', retokenizes=True)
    def tokenizer(doc):
        model, args = tokenizer_model
        model_mwt, args_mwt = mwt_model
        
        with doc.retokenize() as retokenizer:
            retokenizer.merge(doc[0:len(doc)])
        starts = []
        tokens_list = tokenizer.tokenizer(model, args, doc.text)
        tokens_list = mwt.mwt(model_mwt, args_mwt, tokens_list)
        tokens = []
        index = 0
        for l in tokens_list:
            starts.append(index)
            for t in l: 
                tokens.append(t)
                index += 1
        doc = Doc(nlp.vocab, words=tokens)
        spans = []
        for idx, i in enumerate(starts):
            if idx+1 == len(starts):
                spans.append(Span(doc, i, index))
            else:
                spans.append(Span(doc, i, starts[idx+1]))
        doc._.sentences = spans
        
        return doc

    @Language.component('lemmatize', assigns=["token.lemma"])
    def lemmatizer(doc):
        
        model, args = lemma_model
        for sent in doc._.sentences:
            tokens = [d.text for d in sent]
            lemmas = lemmatizer.lemma(model, args, [tokens])
            for idx, d in enumerate(sent): d.lemma_ = lemmas[idx]
        
        return doc
    
    

   
class Pipeline():
    def __new__(cls, pipeline):
        language = NLP('fa', pipeline)
        nlp = language.nlp
        return nlp 

        
def load_pipline(pipelines):
    language = NLP('fa', pipelines)
    nlp = language.nlp
    return nlp

def to_json(pipelines, doc):
    dict_list = []
    for sent in doc._.sentences:
        sentence = []
        for i, d in enumerate(sent):
            dictionary = {}
            dictionary['id'] = i+1
            dictionary['text'] = d.text
            if 'lem' in pipelines: dictionary['lemma'] = d.lemma_
            if 'pos' in pipelines: dictionary['pos'] = d.pos_
            if 'dep' in pipelines: 
                dictionary['rel'] = d.dep_
                dictionary['root'] = d._.dep_arc
            sentence.append(dictionary)
        dict_list.append(sentence)
    return dict_list
 
