import pandas as pd
import numpy as np
import scipy as sp
import re
import nltk
from nltk.corpus import stopwords
from copy import deepcopy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import pairwise_distances
import nltk
import string

import nltk
from nltk.stem import WordNetLemmatizer

from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer

# File location and type
RECO_DATA_1_FILE_LOCATION = "/FileStore/tables/reco_data_1.csv"
FILE_TYPE = "csv"

# CSV options
INFER_SCHEMA = "false"
FIRST_ROW_IS_HEADER = "true"
DELIMITER = ","

    
    
    
class ContentFilter:
    
    def __init__(
        self,
        file_type=FILE_TYPE,
        infer_schema=INFER_SCHEMA,
        first_row_is_header=FIRST_ROW_IS_HEADER,
        delimiter=DELIMITER,
        file_location=RECO_DATA_1_FILE_LOCATION
    ):
        '''
        ...
        '''
        print ('in ContentFilter')
        
        self.file_type = file_type
        self.infer_schema = infer_schema
        self.first_row_is_header = first_row_is_header
        self.delimiter = delimiter
        self.file_location = file_location
        
        self.reco_df = spark.read.format(self.file_type) \
          .option("inferSchema", self.infer_schema) \
          .option("header", self.first_row_is_header) \
          .option("sep", self.delimiter) \
          .load(self.file_location)
        
        
    def run(self):
        
        print ('run...')
        '''
        df1 = reco_df.filter(df["KB_ARTCL_ID"].substr(1, 1) == 'k')
        
        
        #getting total unique words

        pandas_df = df1.toPandas()

        
        #remove_html_tags(data.loc[0][1])
        a = lambda x: str(x)
        pandas_df['KB_ARTCL_SMRY_TXT'] = pandas_df['KB_ARTCL_SMRY_TXT'].apply(a)

        pandas_df['summary_cleaned'] = pandas_df['KB_ARTCL_SMRY_TXT'].apply(lambda x: preprocess_text(x))
        
        
        # wordnet_lemmatizer = WordNetLemmatizer()
        # word1 = wordnet_lemmatizer.lemmatize("runner",pos="v")
        list_of_sentences = pandas_df['summary_cleaned'].tolist() 

        main_dict = {}

        for sentence in list_of_sentences:
          worlist = sentence.split()
          for word in worlist:
            if word in main_dict:
              main_dict[word] = main_dict[word]+1
            else:
              main_dict[word] = 1
        len(main_dict)
    
    
        # print(word1)
        vectorizer = CountVectorizer(analyzer = "word",   \
                                 tokenizer = None,    \
                                 preprocessor = None, \
                                 stop_words = None,   \
                                 max_features = 10000) 


        X_counts = vectorizer.fit_transform(list_of_sentences)
        
        transformer = TfidfTransformer(smooth_idf=False)

        tfidf = transformer.fit_transform(X_counts)

        X_tfidf = tfidf.toarray()

        X_tfidf_list =X_tfidf.tolist()
        pandas_df['tfidf_array'] = X_tfidf_list
        
        pandas_df['Article_ID_int'] = pandas_df['Article_ID'].str.extract('(\d+)', expand=False)
        pandas_df = pandas_df.dropna(subset=['Article_ID_int'])

        pandas_df = pandas_df.drop_duplicates(subset=['Article_ID_int'])
        
    
        pandas_df_1 = pandas_df.set_index('Article_ID_int')
    
    
        # decompose this with if/else and helper functions
        import pandas as pd
        import numpy as np 

        from scipy import spatial


        from numpy.linalg import norm
        import pandas as pd

        df = pd.DataFrame(columns = ['col1', 'col2', 'dotsum'])


        for col1 in pandas_df['Article_ID_int']:
          for col2 in pandas_df['Article_ID_int']:
            str1 = col1+"_"+col2

            if (str1 in common_articles_list)  & (col1 != col2):

              try:
                df = df.append({'col1' : col1, 'col2' : col2, 'dotsum' : 1 - spatial.distance.cosine(pandas_df_1.loc[col1]["tfidf_array"],pandas_df_1.loc[col2]["tfidf_array"])},ignore_index = True)
              except:
                print("cant process: ", str1)
                
                
        # using sparse matrix (in lieu of above)
        
        import scipy
        tfidf_sparse = scipy.sparse.csr_matrix(X_tfidf)
        from scipy.sparse import coo_matrix, hstack, vstack

        from sklearn.metrics.pairwise import cosine_similarity
        from scipy import sparse

        similarities = cosine_similarity(tfidf_sparse)
        print('pairwise dense output:\n {}\n'.format(similarities))

        #also can output sparse matrices
        similarities_sparse = cosine_similarity(tfidf_sparse,dense_output=False)
        print('pairwise sparse output:\n {}\n'.format(similarities_sparse))
        
        pandas_df['index'] = pandas_df.index

        article_id_index = pandas_df[['index','Article_ID']]
        '''
                

    def _preprocess_text(self,text):
        '''
        ...
        '''
        
        pass
        
        '''
        #Write your code below.
    
        # 1. Remove non-letters        
        letters_only = re.sub("[^a-zA-Z]", " ", text) 
        #
        # 2. Convert to lower case, split into individual words
        letters_only1 = letters_only.lower()       

        words = nltk.word_tokenize(letters_only1)

        # 3. In Python, searching a set is much faster than searching
        #   a list, so convert the stop words to a set

        nltk.download('stopwords')
        nltk.download('wordnet')
        sw1 = set(nltk.corpus.stopwords.words('english'))
        sw2 = set(string.ascii_lowercase)
        
        sw3 = set(["a's" , "able" , "about" , "above" , "according" , "accordingly" , "across" , "actually" , "after" , "afterwards" , "again" , "against" , "ain't" , "all" , "allow" , "allows" , "almost" , "alone" , "along" , "already" , "also" , "although" , "always" , "am" , "among" , "amongst" , "an" , "and" , "another" , "any" , "anybody" , "anyhow" , "anyone" , "anything" , "anyway" , "anyways" , "anywhere" , "apart" , "appear" , "appreciate" , "appropriate" , "are" , "aren't" , "around" , "as" , "aside" , "ask" , "asking" , "associated" , "at" , "available" , "away" , "awfully" , "be" , "became" , "because" , "become" , "becomes" , "becoming" , "been" , "before" , "beforehand" , "behind" , "being" , "believe" , "below" , "beside" , "besides" , "best" , "better" , "between" , "beyond" , "both" , "brief" , "but" , "by" , "c'mon" , "c's" , "came" , "can" , "can't" , "cannot" , "cant" , "cause" , "causes" , "certain" , "certainly" , "changes" , "clearly" , "co" , "com" , "come" , "comes" , "concerning" , "consequently" , "consider" , "considering" , "contain" , "containing" , "contains" , "corresponding" , "could" , "couldn't" , "course" , "currently" , "definitely" , "described" , "despite" , "did" , "didn't" , "different" , "do" , "does" , "doesn't" , "doing" , "don't" , "done" , "down" , "downwards" , "during" , "each" , "edu" , "eg" , "eight" , "either" , "else" , "elsewhere" , "enough" , "entirely" , "especially" , "et" , "etc" , "even" , "ever" , "every" , "everybody" , "everyone" , "everything" , "everywhere" , "ex" , "exactly" , "example" , "except" , "far" , "few" , "fifth" , "first" , "five" , "followed" , "following" , "follows" , "for" , "former" , "formerly" , "forth" , "four" , "from" , "further" , "furthermore" , "get" , "gets" , "getting" , "given" , "gives" , "go" , "goes" , "going" , "gone" , "got" , "gotten" , "greetings" , "had" , "hadn't" , "happens" , "hardly" , "has" , "hasn't" , "have" , "haven't" , "having" , "he" , "he's" , "hello" , "help" , "hence" , "her" , "here" , "here's" , "hereafter" , "hereby" , "herein" , "hereupon" , "hers" , "herself" , "hi" , "him" , "himself" , "his" , "hither" , "hopefully" , "how" , "howbeit" , "however" , "i'd" , "i'll" , "i'm" , "i've" , "ie" , "if" , "ignored" , "immediate" , "in" , "inasmuch" , "inc" , "indeed" , "indicate" , "indicated" , "indicates" , "inner" , "insofar" , "instead" , "into" , "inward" , "is" , "isn't" , "it" , "it'd" , "it'll" , "it's" , "its" , "itself" , "just" , "keep" , "keeps" , "kept" , "know" , "known" , "knows" , "last" , "lately" , "later" , "latter" , "latterly" , "least" , "less" , "lest" , "let" , "let's" , "like" , "liked" , "likely" , "little" , "look" , "looking" , "looks" , "ltd" , "mainly" , "many" , "may" , "maybe" , "me" , "mean" , "meanwhile" , "merely" , "might" , "more" , "moreover" , "most" , "mostly" , "much" , "must" , "my" , "myself" , "name" , "namely" , "nd" , "near" , "nearly" , "necessary" , "need" , "needs" , "neither" , "never" , "nevertheless" , "new" , "next" , "nine" , "no" , "nobody" , "non" , "none" , "noone" , "nor" , "normally" , "not" , "nothing" , "novel" , "now" , "nowhere" , "obviously" , "of" , "off" , "often" , "oh" , "ok" , "okay" , "old" , "on" , "once" , "one" , "ones" , "only" , "onto" , "or" , "other" , "others" , "otherwise" , "ought" , "our" , "ours" , "ourselves" , "out" , "outside" , "over" , "overall" , "own" , "particular" , "particularly" , "per" , "perhaps" , "placed" , "please" , "plus" , "possible" , "presumably" , "probably" , "provides" , "que" , "quite" , "qv" , "rather" , "rd" , "re" , "really" , "reasonably" , "regarding" , "regardless" , "regards" , "relatively" , "respectively" , "right" , "said" , "same" , "saw" , "say" , "saying" , "says" , "second" , "secondly" , "see" , "seeing" , "seem" , "seemed" , "seeming" , "seems" , "seen" , "self" , "selves" , "sensible" , "sent" , "serious" , "seriously" , "seven" , "several" , "shall" , "she" , "should" , "shouldn't" , "since" , "six" , "so" , "some" , "somebody" , "somehow" , "someone" , "something" , "sometime" , "sometimes" , "somewhat" , "somewhere" , "soon" , "sorry" , "specified" , "specify" , "specifying" , "still" , "sub" , "such" , "sup" , "sure" , "t's" , "take" , "taken" , "tell" , "tends" , "th" , "than" , "thank" , "thanks" , "thanx" , "that" , "that's" , "thats" , "the" , "their" , "theirs" , "them" , "themselves" , "then" , "thence" , "there" , "there's" , "thereafter" , "thereby" , "therefore" , "therein" , "theres" , "thereupon" , "these" , "they" , "they'd" , "they'll" , "they're" , "they've" , "think" , "third" , "this" , "thorough" , "thoroughly" , "those" , "though" , "three" , "through" , "throughout" , "thru" , "thus" , "to" , "together" , "too" , "took" , "toward" , "towards" , "tried" , "tries" , "truly" , "try" , "trying" , "twice" , "two" , "un" , "under" , "unfortunately" , "unless" , "unlikely" , "until" , "unto" , "up" , "upon" , "us" , "use" , "used" , "useful" , "uses" , "using" , "usually" , "value" , "various" , "very" , "via" , "viz" , "vs" , "want" , "wants" , "was" , "wasn't" , "way" , "we" , "we'd" , "we'll" , "we're" , "we've" , "welcome" , "well" , "went" , "were" , "weren't" , "what" , "what's" , "whatever" , "when" , "whence" , "whenever" , "where" , "where's" , "whereafter" , "whereas" , "whereby" , "wherein" , "whereupon" , "wherever" , "whether" , "which" , "while" , "whither" , "who" , "who's" , "whoever" , "whole" , "whom" , "whose" , "why" , "will" , "willing" , "wish" , "with" , "within" , "without" , "won't" , "wonder" , "would" , "wouldn't" , "yes" , "yet" , "you" , "you'd" , "you'll" , "you're" , "you've" , "your" , "yours" , "yourself" , "yourselves" , "zero"])
    
    

        stops = sw3.union(sw2.union(sw1))

        # 4. Remove stop words
        meaningful_words = [w for w in words if not w in stops]  


        # 5. stem the words
        lancaster=LancasterStemmer()

        new_list = []
        for word in meaningful_words:
          a = lancaster.stem(word)
          new_list.append(a)



        # 6. Join the words back into one string separated by space, 
        # and return the result.


        return( " ".join( new_list ))   
        '''
        
        
        
        
        
        
        
        
    def _preprocess_text_old(self,text):
        '''
        ...
        '''
        
        # 1. Remove non-letters        
        letters_only = re.sub("[^a-zA-Z]", " ", text) 
        #
        # 2. Convert to lower case, split into individual words
        letters_only1 = letters_only.lower()  
        
        
        words = nltk.word_tokenize(letters_only1)

        # 3. In Python, searching a set is much faster than searching
        #   a list, so convert the stop words to a set
        nltk.download('stopwords')
        nltk.download('wordnet')
        
        sw1 = set(nltk.corpus.stopwords.words('english'))
        sw2 = set(string.ascii_lowercase)
        sw3 = set(["a's" , "able" , "about" , "above" , "according" , "accordingly" , "across" , "actually" , "after" , "afterwards" , "again" , "against" , "ain't" , "all" , "allow" , "allows" , "almost" , "alone" , "along" , "already" , "also" , "although" , "always" , "am" , "among" , "amongst" , "an" , "and" , "another" , "any" , "anybody" , "anyhow" , "anyone" , "anything" , "anyway" , "anyways" , "anywhere" , "apart" , "appear" , "appreciate" , "appropriate" , "are" , "aren't" , "around" , "as" , "aside" , "ask" , "asking" , "associated" , "at" , "available" , "away" , "awfully" , "be" , "became" , "because" , "become" , "becomes" , "becoming" , "been" , "before" , "beforehand" , "behind" , "being" , "believe" , "below" , "beside" , "besides" , "best" , "better" , "between" , "beyond" , "both" , "brief" , "but" , "by" , "c'mon" , "c's" , "came" , "can" , "can't" , "cannot" , "cant" , "cause" , "causes" , "certain" , "certainly" , "changes" , "clearly" , "co" , "com" , "come" , "comes" , "concerning" , "consequently" , "consider" , "considering" , "contain" , "containing" , "contains" , "corresponding" , "could" , "couldn't" , "course" , "currently" , "definitely" , "described" , "despite" , "did" , "didn't" , "different" , "do" , "does" , "doesn't" , "doing" , "don't" , "done" , "down" , "downwards" , "during" , "each" , "edu" , "eg" , "eight" , "either" , "else" , "elsewhere" , "enough" , "entirely" , "especially" , "et" , "etc" , "even" , "ever" , "every" , "everybody" , "everyone" , "everything" , "everywhere" , "ex" , "exactly" , "example" , "except" , "far" , "few" , "fifth" , "first" , "five" , "followed" , "following" , "follows" , "for" , "former" , "formerly" , "forth" , "four" , "from" , "further" , "furthermore" , "get" , "gets" , "getting" , "given" , "gives" , "go" , "goes" , "going" , "gone" , "got" , "gotten" , "greetings" , "had" , "hadn't" , "happens" , "hardly" , "has" , "hasn't" , "have" , "haven't" , "having" , "he" , "he's" , "hello" , "help" , "hence" , "her" , "here" , "here's" , "hereafter" , "hereby" , "herein" , "hereupon" , "hers" , "herself" , "hi" , "him" , "himself" , "his" , "hither" , "hopefully" , "how" , "howbeit" , "however" , "i'd" , "i'll" , "i'm" , "i've" , "ie" , "if" , "ignored" , "immediate" , "in" , "inasmuch" , "inc" , "indeed" , "indicate" , "indicated" , "indicates" , "inner" , "insofar" , "instead" , "into" , "inward" , "is" , "isn't" , "it" , "it'd" , "it'll" , "it's" , "its" , "itself" , "just" , "keep" , "keeps" , "kept" , "know" , "known" , "knows" , "last" , "lately" , "later" , "latter" , "latterly" , "least" , "less" , "lest" , "let" , "let's" , "like" , "liked" , "likely" , "little" , "look" , "looking" , "looks" , "ltd" , "mainly" , "many" , "may" , "maybe" , "me" , "mean" , "meanwhile" , "merely" , "might" , "more" , "moreover" , "most" , "mostly" , "much" , "must" , "my" , "myself" , "name" , "namely" , "nd" , "near" , "nearly" , "necessary" , "need" , "needs" , "neither" , "never" , "nevertheless" , "new" , "next" , "nine" , "no" , "nobody" , "non" , "none" , "noone" , "nor" , "normally" , "not" , "nothing" , "novel" , "now" , "nowhere" , "obviously" , "of" , "off" , "often" , "oh" , "ok" , "okay" , "old" , "on" , "once" , "one" , "ones" , "only" , "onto" , "or" , "other" , "others" , "otherwise" , "ought" , "our" , "ours" , "ourselves" , "out" , "outside" , "over" , "overall" , "own" , "particular" , "particularly" , "per" , "perhaps" , "placed" , "please" , "plus" , "possible" , "presumably" , "probably" , "provides" , "que" , "quite" , "qv" , "rather" , "rd" , "re" , "really" , "reasonably" , "regarding" , "regardless" , "regards" , "relatively" , "respectively" , "right" , "said" , "same" , "saw" , "say" , "saying" , "says" , "second" , "secondly" , "see" , "seeing" , "seem" , "seemed" , "seeming" , "seems" , "seen" , "self" , "selves" , "sensible" , "sent" , "serious" , "seriously" , "seven" , "several" , "shall" , "she" , "should" , "shouldn't" , "since" , "six" , "so" , "some" , "somebody" , "somehow" , "someone" , "something" , "sometime" , "sometimes" , "somewhat" , "somewhere" , "soon" , "sorry" , "specified" , "specify" , "specifying" , "still" , "sub" , "such" , "sup" , "sure" , "t's" , "take" , "taken" , "tell" , "tends" , "th" , "than" , "thank" , "thanks" , "thanx" , "that" , "that's" , "thats" , "the" , "their" , "theirs" , "them" , "themselves" , "then" , "thence" , "there" , "there's" , "thereafter" , "thereby" , "therefore" , "therein" , "theres" , "thereupon" , "these" , "they" , "they'd" , "they'll" , "they're" , "they've" , "think" , "third" , "this" , "thorough" , "thoroughly" , "those" , "though" , "three" , "through" , "throughout" , "thru" , "thus" , "to" , "together" , "too" , "took" , "toward" , "towards" , "tried" , "tries" , "truly" , "try" , "trying" , "twice" , "two" , "un" , "under" , "unfortunately" , "unless" , "unlikely" , "until" , "unto" , "up" , "upon" , "us" , "use" , "used" , "useful" , "uses" , "using" , "usually" , "value" , "various" , "very" , "via" , "viz" , "vs" , "want" , "wants" , "was" , "wasn't" , "way" , "we" , "we'd" , "we'll" , "we're" , "we've" , "welcome" , "well" , "went" , "were" , "weren't" , "what" , "what's" , "whatever" , "when" , "whence" , "whenever" , "where" , "where's" , "whereafter" , "whereas" , "whereby" , "wherein" , "whereupon" , "wherever" , "whether" , "which" , "while" , "whither" , "who" , "who's" , "whoever" , "whole" , "whom" , "whose" , "why" , "will" , "willing" , "wish" , "with" , "within" , "without" , "won't" , "wonder" , "would" , "wouldn't" , "yes" , "yet" , "you" , "you'd" , "you'll" , "you're" , "you've" , "your" , "yours" , "yourself" , "yourselves" , "zero"])

        stops = sw3.union(sw2.union(sw1))

        # 4. Remove stop words
        meaningful_words = [w for w in words if not w in stops]  


        # 5. stem the words
        lancaster=LancasterStemmer()

        new_list = []
        for word in meaningful_words:
          a = lancaster.stem(word)
          new_list.append(a)



        # 6. Join the words back into one string separated by space, 
        # and return the result.
        return( " ".join( new_list ))   
        
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
