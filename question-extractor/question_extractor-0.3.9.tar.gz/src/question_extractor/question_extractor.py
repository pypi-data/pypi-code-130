import pandas as pd
#from IPython.display import Image, display
import numpy as np
import re
import string
import datetime
import pickle
import os
import time
import math
from collections import Counter
import pkg_resources


import keras
#from keras.models import Sequential
#from keras.layers import Dense, Dropout, Activation
#from keras.preprocessing.text import Tokenizer
#from keras_preprocessing.sequence import pad_sequences
#from keras_preprocessing import sequence
#from keras.layers import Embedding, LSTM

import tensorflow as tf
from tensorflow import keras
#from tensorflow.keras.layers import Embedding
from tensorflow.keras.layers import TextVectorization
#from tensorflow.keras import layers
from keras.models import load_model

#from gensim.models import Word2Vec
#from tqdm import tqdm
#tqdm.pandas()



DATA_PATH1 = pkg_resources.resource_filename('question_extractor', 'data/no_context_question_sentences.txt')
DATA_PATH2 = pkg_resources.resource_filename('question_extractor', 'models/cnn_model_v2_40K.h5')
DATA_PATH3 = pkg_resources.resource_filename('question_extractor', 'models/vectorizer_v2_40K.pkl')


def clean_text(text):
    '''Make text lowercase, remove text in square brackets,remove links,remove punctuation
    and remove words containing numbers.'''
    text = str(text).lower()
    text = text.strip()
    text = re.sub('[^a-zA-Z ]', '', text)
    text = text.replace('“','"').replace('”','"')
    text = re.sub("[\"\']", "", text)
    text = re.sub('\[.*?-\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = " ".join(text.split())
    text = text.strip()
    #text = ' '.join(e.lower() for e in text.split() if e.lower() not in stopwords)
    return text



class predict_sentence():

    def __init__(self, model_path, vectorizer_path, class_names):

        """
        Init function
        
        Args:
            model_path: string containing path of trained model
            vectorizer_path: string containing path of word2vec model
            class_names: list of class names in string 
        """
    
        self.class_names = class_names

        from_disk = pickle.load(open(vectorizer_path, "rb"))
        vectorizer = TextVectorization.from_config(from_disk['config'])
        vectorizer.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
        vectorizer.set_weights(from_disk['weights'])
        
        
        model = load_model(model_path)

        string_input = keras.Input(shape=(1,), dtype="string")
        x = vectorizer(string_input)
        preds = model(x)
        end_to_end_model = keras.Model(string_input, preds)
        
        self.end_to_end_model = end_to_end_model


    def predict(self, predict_data, batch=False):

        """
        predicts data from loaded model

        Args:
           predict_data: list of sentences

        Returns:
           array of predictions
        """
        
        probabilities = self.end_to_end_model.predict([[predict_data]])
        return self.class_names[np.argmax(probabilities[0])]
    

    
def extract_question(x, model):

    """
    main function in extracting questions
    takes are paragraph, split them into sentences and checks if a sentence is question or not

    Args:
        model: ML model object
        
    return:
        list of questions if there are any in a particular case description, if there ain't any it returns np.nan
    """

    raw_sentences = re.split('[ ]*[.?!|•;\n]+[ \n]*', x)
    

    questions = [] #output list of questions
    for element in raw_sentences:
        element = clean_text(element)
        if model.predict([element]) == "Question": #check if the sentence is a question
            questions.append(element) #if so, add it to the list

    if questions:
        return questions
    else:
        np.nan

  
with open(DATA_PATH1, 'r', encoding='cp1252') as f:
    no_context_filter = [line.rstrip('\n') for line in f]
        
whwords = ['who', 'what', 'whats', 'whos', 'where', 'when', 'why', 'how', 'which', 'whose', 'whence', 'whither', 'whom']
begin_question_word = ["can", "could"] 

question_pattern = ["do i", "do you have", "do you know", "does at", "do we",
                    "is it", "is it so", "is this true", "is that true", "is there", 
                    "could you", "could i", "could it", "could someone", "could the",
                    "would you", "would there",
                    "may i",
                    "are there", "are we", "are any", "are these",
                    "am i", "to know", "to whom", "to who",
                    "can i", "can we", "can you", "can it be", "can the", "can someone",
                    "tell me more", "tell me",
                    "please could", "please can", "please would", "please may",
                    "question", "question is", "answer", "questions", "answers", "ask",
                    "how many", "how much", "how to", 
                    "what is", "what are", 
                    "why is", "why are",
                    "who is", "who are",
                    "where is", 
                    "when will", "what will"]

helping_verbs = ["is", "am", "can", "are", "do", "does"]

scolding_setences1 = ["what the", "what a", "where as", "how dare", "how unfair", "which seems", "which i", "why cant", "why not"]
scolding_setences2 = ["what is the point", "no idea why"]

WORD = re.compile(r"\w+")


def words_to_ngrams(words, n, sep=" "):
    return [sep.join(words[i:i+n]) for i in range(len(words)-n+1)]


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def get_cosine(text1, text2):
    vec1 = text_to_vector(text1)
    vec2 = text_to_vector(text2)
    
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def is_question_post_filter(text):

    is_ques = False
    if len(text.split(' ')) > 2:
        if text.split(' ')[0] in begin_question_word:
            is_ques = True

        elif text.split(' ')[0] in whwords or text.split(' ')[1] in whwords:
            if " ".join(text.split(' ')[0:2]) not in scolding_setences1 and any(x not in text for x in scolding_setences2):
                is_ques = True

        elif text.split(' ')[1] in whwords:
            if " ".join(text.split(' ')[1:3]) not in scolding_setences1 and any(x not in text for x in scolding_setences2):
                is_ques = True

        else: 
            for pattern in question_pattern:
                ngrams_list = words_to_ngrams(text.split(' '), len(pattern.split(' ')))
                if pattern in ngrams_list and len(text.split(' ')) > len(pattern.split(' ')) + 1:
                    is_ques = True
                    break

        if is_ques:
            for sent_ in no_context_filter:
                if get_cosine(sent_, text) > .75:
                    return 0
        else:
            return 0


        return 1
          
          
def load_model_():
    class_names = ['Question', 'Statement']
    model = predict_sentence(DATA_PATH2, DATA_PATH3, class_names)
    return model