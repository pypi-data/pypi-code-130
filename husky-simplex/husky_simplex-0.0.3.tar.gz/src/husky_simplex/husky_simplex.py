import numpy as np 
import string
from multipledispatch import dispatch
import re
from collections import Counter
from scipy.sparse import csr_matrix
import pandas as pd
import math

# Sudhendra's part
def __modify(input_str):
    if type(input_str) == tuple or type(input_str) == list:
        if type(input_str) == tuple:
            input_str = list(input_str)
        input_str = ' '.join(input_str)
    return input_str

class Word:
    def __init__(self, input_str = None):
        
        self.input_str = input_str
        if type(self.input_str) == tuple or type(self.input_str) == list:
            if type(self.input_str) == tuple:
                self.input_str = list(self.input_str)
                self.temp = list(self.input_str)
            elif type(self.input_str) == list:
                self.temp = self.input_str
            self.input_str = ' '.join(self.input_str)
        elif type(self.input_str) == str:
            self.temp = [self.input_str]
        
        self.STOPWORDS = [
            'those', 'on', 'own', '’ve', 'yourselves', 'around', 'between', 'four', 'been', 'alone', 
            'off', 'am', 'then', 'other', 'can', 'regarding', 'hereafter', 'front', 'too', 'used', 
            'wherein', '‘ll', 'doing', 'everything', 'up', 'onto', 'never', 'either', 'how', 'before', 
            'anyway', 'since', 'through', 'amount', 'now', 'he', 'was', 'have', 'into', 'because', 
            'not', 'therefore', 'they', 'n’t', 'even', 'whom', 'it', 'see', 'somewhere', 'thereupon', 
            'nothing', 'whereas', 'much', 'whenever', 'seem', 'until', 'whereby', 'at', 'also', 'some', 
            'last', 'than', 'get', 'already', 'our', 'once', 'will', 'noone', "'m", 'that', 'what', 
            'thus', 'no', 'myself', 'out', 'next', 'whatever', 'although', 'though', 'which', 'would', 
            'therein', 'nor', 'somehow', 'whereupon', 'besides', 'whoever', 'ourselves', 'few', 'did', 
            'without', 'third', 'anything', 'twelve', 'against', 'while', 'twenty', 'if', 'however', 
            'herself', 'when', 'may', 'ours', 'six', 'done', 'seems', 'else', 'call', 'perhaps', 
            'had', 'nevertheless', 'where', 'otherwise', 'still', 'within', 'its', 'for', 'together', 
            'elsewhere', 'throughout', 'of', 'others', 'show', '’s', 'anywhere', 'anyhow', 'as', 'are', 
            'the', 'hence', 'something', 'hereby', 'nowhere', 'latterly', 'say', 'does', 'neither', 
            'his', 'go', 'forty', 'put', 'their', 'by', 'namely', 'could', 'five', 'unless', 'itself', 
            'is', 'nine', 'whereafter', 'down', 'bottom', 'thereby', 'such', 'both', 'she', 'become', 
            'whole', 'who', 'yourself', 'every', 'thru', 'except', 'very', 'several', 'among', 'being', 
            'be', 'mine', 'further', 'n‘t', 'here', 'during', 'why', 'with', 'just', "'s", 'becomes', 
            '’ll', 'about', 'a', 'using', 'seeming', "'d", "'ll", "'re", 'due', 'wherever', 'beforehand', 
            'fifty', 'becoming', 'might', 'amongst', 'my', 'empty', 'thence', 'thereafter', 'almost', 
            'least', 'someone', 'often', 'from', 'keep', 'him', 'or', '‘m', 'top', 'her', 'nobody', 
            'sometime', 'across', '‘s', '’re', 'hundred', 'only', 'via', 'name', 'eight', 'three', 
            'back', 'to', 'all', 'became', 'move', 'me', 'we', 'formerly', 'so', 'i', 'whence', 'under', 
            'always', 'himself', 'in', 'herein', 'more', 'after', 'themselves', 'you', 'above', 'sixty', 
            'them', 'your', 'made', 'indeed', 'most', 'everywhere', 'fifteen', 'but', 'must', 'along', 
            'beside', 'hers', 'side', 'former', 'anyone', 'full', 'has', 'yours', 'whose', 'behind', 
            'please', 'ten', 'seemed', 'sometimes', 'should', 'over', 'take', 'each', 'same', 'rather', 
            'really', 'latter', 'and', 'ca', 'hereupon', 'part', 'per', 'eleven', 'ever', '‘re', 'enough', 
            "n't", 'again', '‘d', 'us', 'yet', 'moreover', 'mostly', 'one', 'meanwhile', 'whither', 'there', 
            'toward', '’m', "'ve", '’d', 'give', 'do', 'an', 'quite', 'these', 'everyone', 'towards', 
            'this', 'cannot', 'afterwards', 'beyond', 'make', 'were', 'whether', 'well', 'another', 
            'below', 'first', 'upon', 'any', 'none', 'many', 'serious', 'various', 're', 'two', 'less', '‘ve'
        ]
    
    def extend_words(self, words):
        self.STOPWORDS.append(words)
    
    def remove_words(self, words):
        unwanted = set(words)
        new_words = [item for item in self.STOPWORDS if item not in unwanted]
        self.STOPWORDS = new_words

    def tokenize(self):
        """
        Tokenize the input string(s)
        returns: list of tokens
        Usage: string.tokenize() where string is an instance of Word class.
        """
        token = self.input_str.split()
        return token
    
    def word_counter(self):
        """
        Count the number of words in a string.
        returns: list of words and their respective integer count(s)
        Usage: string.word_counter() where string is an instance of Word class.
        """
        words = self.tokenize()
        words = np.array(words)
        dictionary = {}
        for word in words:
            index = np.where( words == word)
            index = np.array(index).flatten()
            dictionary[word] = len(index)
        count = []
        for key, value in dictionary.items():
            temp = [key, value]
            count.append(temp)
        return count
    
    def remove_stopwords(self):
        """
        Removes stopwords from a string.
        returns: A list type, containing tokens with the stopwords removed
        Usage: string.remove_stopwords() where string is an instance of Word class.
        NOTE: Use extend_words(words) and remove_words(words) methods of Word class to modify STOPWORDS.
        """
        tokens = [each.split() for each in self.temp]
        words = []
        for strings in tokens:
            words.append([item for item in strings if item.lower() not in self.STOPWORDS])
        return words
    
    def join_stopwords(self):
        """
        Generate a new string without stopwords.
        returns: A list of strings without the stopwords.
        Usage: string.join_stopwords() where string is an instance of Word class.
        """
        words = self.remove_stopwords()
        new_text = []
        for each in words:
            new_text.append(" ".join(each))
        return new_text
# Sudhendra's end 

#Karans Part
class Clean:

    @dispatch(str)
    def remove_punctuation(s):
        """
        1) To remove punctuations from string.
        2) s: string input parameter
        3) returns string with no punctuations.
        """
        c = ""
        for i in s:
            if i == '/':
                c+=" " 
          
            elif i not in string.punctuation:
                c+=i                    

        return c

    @dispatch(list)
    def remove_punctuation(s):
        """
        1) To remove punctuations from a list of strings.
        2) s: list input parameter
        3) returns list of strings with no punctuation.
        """
        for i in range(len(s)):
            c = ""
            for t in s[i]:
                if t == '/':
                    c+=" "
                elif t not in string.punctuation:
                    c+=t
            s[i] = c

        return s
    
    @dispatch(list)
    def stem(t):
        """
        1) To remove tense and grammatical suffixes from words.
        2) t: A list of strings. Input parameter.
        3) returns list of strings that have been stemmed.
        """
        l = []
        for w in t:
            if w.endswith('ical'):
                l.append(w.replace('ical','ic'))

            elif w.endswith('ies'):
                l.append(w.replace('ies','y'))

            elif w.endswith('eed'):
                l.append(w.replace('eed','ee'))

            elif w.endswith('sses'):
                l.append(w.replace('sses','ss'))

            elif w.endswith('ization'):
                l.append(w.replace('ization','ize'))

            elif w.endswith('ation'):
                l.append(w.replace('ation','ate'))

            elif w.endswith('iveness'):
                l.append(w.replace('iveness','ive'))

            elif w.endswith('fulness'):
                l.append(w.replace('fulness','ful'))

            elif w.endswith('ousness'):
                l.append(w.replace('ousness','ous'))

            elif w.endswith('ality'):
                l.append(w.replace('ality','al'))

            elif w.endswith('ivity') or w.endswith('bility') or w.endswith('ability'):
                l.append(re.sub('(ivity|ability|bility)$','',w))

            elif w.endswith('cacy'):
                l.append(w.replace('cacy','cate'))

            elif w.endswith('icity'):
                l.append(w.replace('icity','e'))

            elif w.endswith('alize'):
                l.append(w.replace('alize','al'))

            elif w.endswith('ence') or w.endswith('er') or w.endswith('ize') or w.endswith('ent') or w.endswith('ible') or w.endswith('able') or w.endswith('ance') or w.endswith('ness') or w.endswith('less') or w.endswith('ship') or w.endswith('ing') or w.endswith('er') or w.endswith('ers')  or w.endswith('ly') or w.endswith('ment') or w.endswith('al') or w.endswith('ed') or w.endswith('ance') or w.endswith('ful') or w.endswith('ism') or w.endswith('liness') or w.endswith('s'):
                l.append(re.sub('(ence|er|ize|ent|ible|able|ance|ness|less|ship|ing|ly|ers|ment|al|ed|ance|ful|ism|liness|s)$','',w))
                
            else:
                l.append(w)
                
        return l
    
    @dispatch(str)
    def stem(t):
        """
        1) To remove tense and grammatical suffixes from words.
        2) t: string. Input parameter.
        3) returns string that has been stemmed.
        """
        inp = t.split()
        l = []
        for w in inp:
            if w.endswith('ical'):
                l.append(w.replace('ical','ic'))

            elif w.endswith('ies'):
                l.append(w.replace('ies','y'))

            elif w.endswith('eed'):
                l.append(w.replace('eed','ee'))

            elif w.endswith('sses'):
                l.append(w.replace('sses','ss'))

            elif w.endswith('ization'):
                l.append(w.replace('ization','ize'))

            elif w.endswith('ation'):
                l.append(w.replace('ation','ate'))

            elif w.endswith('iveness'):
                l.append(w.replace('iveness','ive'))

            elif w.endswith('fulness'):
                l.append(w.replace('fulness','ful'))

            elif w.endswith('ousness'):
                l.append(w.replace('ousness','ous'))

            elif w.endswith('ality'):
                l.append(w.replace('ality','al'))

            elif w.endswith('ivity') or w.endswith('bility') or w.endswith('ability'):
                l.append(re.sub('(ivity|ability|bility)$','',w))

            elif w.endswith('cacy'):
                l.append(w.replace('cacy','cate'))

            elif w.endswith('icity'):
                l.append(w.replace('icity','e'))

            elif w.endswith('alize'):
                l.append(w.replace('alize','al'))

            elif w.endswith('ence') or w.endswith('er') or w.endswith('ize') or w.endswith('ent') or w.endswith('ible') or w.endswith('able') or w.endswith('ance') or w.endswith('ness') or w.endswith('less') or w.endswith('ship') or w.endswith('ing') or w.endswith('er') or w.endswith('ers')  or w.endswith('ly') or w.endswith('ment') or w.endswith('al') or w.endswith('ed') or w.endswith('ance') or w.endswith('ful') or w.endswith('ism') or w.endswith('liness') or w.endswith('s'):
                l.append(re.sub('(ence|er|ize|ent|ible|able|ance|ness|less|ship|ing|ly|ers|ment|al|ed|ance|ful|ism|liness|s)$','',w))
                
            else:
                l.append(w)
                
        s = " ".join(l)
        return s
    
#Arya's Part	
    @dispatch(str)
    def remove_symbol(st):
        """ 
        Removes Symbols from a String 
        Input: A String containing symbols
        returns: A String without symbols
        Usage: ObjectName.remove_symbol(String), where x is an instance of class Clean 
        """
        pattern = r"""[^A-Za-z0-9 ,.']+"""
        st1 = re.sub(pattern,'',st)
        return st1

    @dispatch(list)
    def remove_symbol(st):
        """ 
        Removes Symbols from all the Strings in the given list
        Input: A list of Strings containing Symbols
        returns: A List of Strings without symbols
        Usage: ObjectName.remove_symbol(List), where x is an instance of class Clean 
        """
        st1 = []
        for x in range(len(st)):
            pattern = r"""[^A-Za-z0-9 ,.']+"""
            st1.append(re.sub(pattern,'',st[x]))
        return st1
    
## Nikhils Part 
def Vectorizer_Clean(input_str,stem = None):
    """
    Removes symbol, punctuation, stopwords and also does stemming of the input if user passes "yes" to stem variable in calss vectorization
    Variables 1] Input_str: takes list as input 
              2] Stem takes string value in either 'yes' or 'no'. Default value 'None' is nothing is passed
    returns: A list of string without punctuation, symbol and stopwords and also stemmed depending on input 
    """  
    c = Clean()
    symbol_removed = c.remove_symbol(input_str)
    punctuation_removed = c.remove_punctuation(symbol_removed)
    
    w = Word(punctuation_removed)
    stopwords_removed = w.join_stopwords() 
    
    if stem == 'yes':
        stemed_list=[]
        x = Clean()
        
        for sentence in stopwords_removed:
            s = x.stem(sentence)
            stemed_list.append(s)
            
        return stemed_list
    
    return stopwords_removed 

class Vectorizer:
    def __init__(self, input_str = None, stem = None):
        
        self.input_str = input_str
        self.stem = stem
        
        if type(self.input_str) == tuple:
            self.input_str = list(self.input_str)
            
        elif type(self.input_str) == str:
            self.input_str = self.input_str.split(". ")
            
        if(self.input_str == None):
            pass
        else:    
            if self.stem != None:
                self.stem = self.stem.lower()
                self.input_str = Vectorizer_Clean(self.input_str, self.stem)
            else:    
                self.input_str = Vectorizer_Clean(self.input_str)
        
            word = Word(self.input_str)
            List_Keys_values = word.word_counter()
            self.vocab  = np.array(List_Keys_values)[:,0]
            
    def BOW_fit_transform(self):
        """
        Creates a matrix with strings as rows and words as columns. This array would consist of frequency of words present in each string. 
        Before creating matrix the input will be passsed through Vectorizer_Clean function to remove symbols, punctuations, stopwords and also stemming will be done on input 
        if user passes stem input while intizialing class Vectorizer.
        returns: A array with frequency of words.
        Usage: ObjectName.BOW_fit_transform() where Vectorize is an instance of Vectorizer class.
        """

        array = np.zeros((len(self.input_str),len(self.vocab)), dtype = int)
        i = 0
        for sentence in self.input_str:
            # array[i][0] = sentence

            sentence = sentence.split(" ")
            sentence = np.array(sentence)
            j = 0
            for word in self.vocab:
                index = np.where(sentence == word)
                index = np.array(index)
                index = index.flatten()
                if np.size(index)==0:
                    array[i][j]=0
                else:
                    array[i][j]= len(index)
                j+=1 
            i+=1
        return array
    
    def BOW_transform(self, test_str):        
        """
        Creates a matrix with strings as rows and words as columns.The list of words is generated using the values passed while creating the object.
        Before creating matrix the input will be passsed through Vectorizer_Clean function to remove symbols, punctuations, stopwords and also to stem input depending on the user's choice.
        This array would consist of frequency of words which is present in the list of words and input string. 
        Input - A string of list 
        returns: A array with frequency of words.
        Usage: ObjectName.BOW_transform(input) where Vectorize is an instance of Vectorizer class.
        """
        
        if (type(test_str) == tuple )or (type(test_str) == str ):
            
            if type(test_str) == tuple:
                test_str = list(test_str)
                
            else:
                test_str = test_str.split(". ")
        
        if self.stem == 'yes':
            test_str = Vectorizer_Clean(test_str,self.stem)
            
        else:            
            test_str = Vectorizer_Clean(test_str)
                
        array = np.zeros((len(test_str),len(self.vocab)), dtype = int)
        i = 0
        for sentence in test_str:
            sentence = sentence.split(" ")
            sentence = np.array(sentence)
            j = 0
            for word in self.vocab:
                index = np.where(sentence == word)
                index = np.array(index)
                index = index.flatten()
                if np.size(index)==0:
                    array[i][j]=0
                else:
                    array[i][j]= len(index)
                j+=1
            i+=1
        return array
    
#Arya's Part
    def cvfit(self,data):
        unique = set()
        for sent in data:
            for word in sent.split(' '):
                if len(word) >= 2:
                    unique.add(word)

        vocab = {}
        for index,word in enumerate(sorted(list(unique))):
            vocab[word] = index
        return vocab


    def cv_trans(self):
        """
        Creates an matrix containing count of words in a string, i.e Vectorization of text based on term frequency
        Input: A List of strings
        Returns: A matrix containing vectorization of text, where no of rows are the sentences and columns are unique words present in all the Strings.
        Usage: ObjectName.custom_trans(data), where Vectorize is instance of class
        """
        data = [x.lower() for x in self.input_str]
        vocab = self.cvfit(data)
        row,col,val = [],[],[]
        for ind,sent in enumerate(data):
            count_word = dict(Counter(sent.split(' ')))
            for word,count in count_word.items():
                if len(word) >= 2:
                    col_index = vocab.get(word)
                    if col_index >=0:
                        row.append(ind)
                        col.append(col_index)
                        val.append(count)
        x = csr_matrix((val, (row,col)), shape=(len(data),len(vocab))).toarray() #Creating Sparse Matrix Representation for Count Vectorization
        return x


#Harshal's part    
    def __preprocessingCorpus(self, corpus, test_str = None):
        """
        Preprocesses the input like tokenization, stop word removal
        Input : A list of string
        Output : A dictionary with word count 
        """
        if(test_str == None):
            combCorpus = ' '.join(self.input_str)
        else:
            combCorpus = ' '.join(test_str)

        word = Word(combCorpus)
        corpus_split = word.tokenize()       
        corpus_processed = word.remove_stopwords()
        corpus_processed = np.array(corpus_processed).flatten()
        corpus_processed = set(corpus_processed)

        sent = Word(corpus)
        sentSplit = sent.tokenize()       
        sentProcessed = sent.remove_stopwords()
        sentProcessed = np.array(sentProcessed).flatten()
        sentProcessed = set(sentProcessed)

        wordDict = dict.fromkeys(corpus_processed, 0)

        for word in sentProcessed:
            wordDict[word]+=1

        return wordDict


    def __calculateTF(self, corpus, test_str = None):
        """
        Calculates Term-frequency 
        Input : A string
        Output : A dictionary containing Term-Frequency
        
        """
        word = Word(corpus)
        corpus_split = word.tokenize()

        wordDict = Vectorizer.__preprocessingCorpus(self, corpus, test_str)

        wordCount = len(corpus_split)
        wordTf = {}

        for word in wordDict.keys():
            wordTf[word] = wordDict[word] / float(wordCount)

        return(wordTf)   


    def __calculateIDF(self, corpus, test_str = None):
        """
        Calculates Inverse Document-Frequency
        Input : A dictionary
        Output : A dictionary containing Inverse Document-Frequency
        """
        wordDf = {}
        wordIdf = {}
        N = len(corpus)

        wordDf = dict.fromkeys(corpus[0].keys(), 0)

        if(test_str == None):
            inputStr = self.input_str
            inputSize = len(self.input_str)
        else:
            inputStr = test_str
            inputSize = len(test_str)
                   
        for word in wordDf:
            df = 0
 
            for i in range(inputSize):
                if word in inputStr[i].split():
                    df += 1
   
            wordIdf[word] = math.log10(N / df )       

        return wordIdf    


    def tfIdf_fit_transform(self):
        """
        Calculates Tf (Term-frequency) - Idf (Inverse Document-Frequency). The tf-idf is calculated using the values passed while creating the object.
        Output : Tf-Idf matrix
        Usage : ObjectName.tfIdfVectorization() where Vectorize is an instance of Class_Vectorization class
        """
        wordDict = []
        tf = []
        idf = {}  
        tfIDfList = []

        for i in range(len(self.input_str)):
            sent = self.input_str[i]
            tf.append( Vectorizer.__calculateTF(self, sent))
            wordDict.append(Vectorizer.__preprocessingCorpus(self, sent))

        idf = Vectorizer.__calculateIDF(self, wordDict)

        for i in range(len(self.input_str)):
            tfIdf = {}
            for word, value in tf[i].items():
                tfIdf[word] = value * idf[word]
   
            tfIDfList.append(tfIdf)  
    
        sortedList = []    
        for d in tfIDfList:            
            sortedList.append(dict( sorted(d.items(), key=lambda x: x[0].lower()) )) 

        output = pd.DataFrame(sortedList)
        
        return output    


    def tfIdf_transform(self, test_str):
        """
        Calculates Tf (Term-frequency) - Idf (Inverse Document-Frequency). The tf-idf is calculated using the values passed.
        Output : Tf-Idf matrix
        Usage : ObjectName.tfIdfVectorization() where Vectorize is an instance of Class_Vectorization class
        """
        
        if (type(test_str) == tuple )or (type(test_str) == str ):
            
            if type(test_str) == tuple:
                test_str = list(test_str)
                
            else:
                test_str = test_str.split(". ")
                
        test_str = Vectorizer_Clean(test_str)    
        
        wordDict = []
        tf = []
        idf = {}  
        tfIDfList = []

        for i in range(len(test_str)):
            sent = test_str[i]
            print(sent)
            tf.append(Vectorizer.__calculateTF(self, sent, test_str))
            wordDict.append(Vectorizer.__preprocessingCorpus(self, sent, test_str))

        idf = Vectorizer.__calculateIDF(self, wordDict, test_str)

        for i in range(len(test_str)):
            tfIdf = {}
            for word, value in tf[i].items():
                tfIdf[word] = value * idf[word]
   
            tfIDfList.append(tfIdf)    

        sortedList = []    
        for d in tfIDfList:            
            sortedList.append(dict( sorted(d.items(), key=lambda x: x[0].lower()) )) 

        output = pd.DataFrame(sortedList)

        return output
