import nltk
import torch
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.porter import *
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams
nltk.download('words')
from nltk.corpus import words

correct_words = words.words()

class Preprocess:
    def __init__(self):
        print("Preprocess instance initialized..")

    def sentence_tokenize(self,txt):
        nltk_tokens = nltk.sent_tokenize(txt)
        print (nltk_tokens)

    def word_tokenize(self,line):
        nltk_tokens = nltk.word_tokenize(line)
        print (nltk_tokens)

    def stopword_removal(self, line):
        stopWords = set(stopwords.words('english'))
        words = word_tokenize(line)
        wordsFiltered = []
        for w in words:
            if w not in stopWords:
                wordsFiltered.append(w)
        print(wordsFiltered)

    # Text Normalization
    # Tokenization → Stemming → Lemmatization → Remove stopwords → Remove punctuation
    def text_normalize(self, line):
        p_stemmer = PorterStemmer()

        # Tokenization
        nltk_tokenList = word_tokenize(line)

        # Stemming
        nltk_stemedList = []
        for word in nltk_tokenList:
            nltk_stemedList.append(p_stemmer.stem(word))

        # Lemmatization
        wordnet_lemmatizer = WordNetLemmatizer()
        nltk_lemmaList = []
        for word in nltk_stemedList:
            nltk_lemmaList.append(wordnet_lemmatizer.lemmatize(word))

        print("\n1] Stemming + Lemmatization:")
        print(nltk_lemmaList)
        # Filter stopword
        filtered_sentence = []
        nltk_stop_words = set(stopwords.words("english"))
        for w in nltk_lemmaList:
            if w not in nltk_stop_words:
                filtered_sentence.append(w)
        # Removing Punctuation
        punctuations = "?:!.,;"
        for word in filtered_sentence:
            if word in punctuations:
                filtered_sentence.remove(word)
        print(" ")
        print("2] Remove stopword & Punctuation:")
        print(filtered_sentence)

        # Cleaning / Preprocessing includes:
        # 1. Lowercasing, not for Marathi
        # 2. Removing Extra Whitespaces
        # 3. Tokenization
        # 4. Spelling Correction
        # 5. Stopwords Removal
        # 6. Removing Punctuations
        # 7. Removal of Frequent Words
        # 8. Stemming
        # 9. Lemmatization
        # 10. Removal of URLs
        # 11. Removal of HTML Tags

        #Classes : Preprocess
    def toLower(self, line):
        print(line.lower())

    def ext_whitespaces_removal(self, line): #extra whitespace removal
        result = re.sub(' +', ' ', line)
        print(str(result))

    def spelling_correction(self, line):
        incorrect_words = line.split()
        for word in incorrect_words:
            temp = [(jaccard_distance(set(ngrams(word, 2)),
                                      set(ngrams(w, 2))), w)
                    for w in correct_words if w[0] == word[0]]
            print(sorted(temp, key=lambda val: val[0])[0][1])

class MahaSent:
    def __init__(self):
        print("MahaSent instance initialized..")

    def sent_analyse(self,txt):
        model_name = "l3cube-pune/MarathiSentiment"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)
        print(classifier(txt))