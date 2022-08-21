import re
from string import punctuation,ascii_uppercase,ascii_lowercase
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


class Tokenizer:
    stop_words = set(stopwords.words('english'))-{'will'}
    re_spaces = re.compile(r'\s+')
    translate_table = str.maketrans(ascii_uppercase+punctuation,ascii_lowercase+' '*len(punctuation))
    wlm = WordNetLemmatizer()
    del translate_table[ord('_')]

    def __init__(self, **kwargs):
        self.tokenize_method = kwargs.get('tokenize_method','simple')

    def compound_keywords(self,keyword_query):
        return [self.tokenize(segment) for segment in keyword_query.split('"')[1::2]]

    def keywords(self,keyword_query):
        return self.tokenize(keyword_query)
    
    def text_translator(self, text):
        keywords = []
        split_text = text.split(' ')
        for word in split_text:
            # translate_table = word.maketrans(punctuation, len(punctuation) * ' ')
            # word = word.translate(translate_table)
            # word = word.strip()
            word = word.replace(',', '')
            # word = word.strip('.')
            word = word.strip()
            keywords.append(word.lower())
        
        return keywords

    def tokenize(self,text):
        if self.tokenize_method == 'simple':
            return [keyword
                    for keyword in self.text_translator(str(text))
                    if keyword not in Tokenizer.stop_words
            ]

        if self.tokenize_method == 'nltk':
            word_tokens = word_tokenize(text)
            keywords = [w for w in word_tokens if not w in self.stop_words]
            return keywords

    def extract_keywords(self, keyword_query):
        compound_operators_indexes = []
        valid_keyword_query = []
        compound_keyword_positions = []

        keywords = keyword_query.split(' ')
        keyword_query_length = len(keywords)

        for keyword_position, keyword in enumerate(keywords):
            keyword = keyword.lower()
            keyword = keyword.replace(',', '')
            keyword = keyword.strip()

            if keyword in Tokenizer.stop_words:
                continue

            if keyword == '+':
                if (keyword_position - 1) in compound_keyword_positions:
                    raise Exception(
                        'Unable to process query due to multiple operands for compound operator')
                
                if (keyword_position - 1) < 0 or\
                        (keyword_position + 1) > (keyword_query_length - 1):
                    raise Exception('Missing operand for compound operator')

                compound_operators_indexes.append(
                    keyword_position,
                )

                valid_keyword_query.append(
                    [keywords[keyword_position - 1],
                        keywords[keyword_position + 1]],
                )

                compound_keyword_positions.extend(
                    [keyword_position - 1, keyword_position + 1],
                )

                continue

            if keyword_position not in compound_keyword_positions:
                if (keyword_position + 1) < keyword_query_length and keywords[keyword_position + 1] == '+':
                    continue

                valid_keyword_query.append(
                    keyword,
                )

        return valid_keyword_query

if __name__ == "__main__":
    t = Tokenizer()

    q = t.extract_keywords(
        "ariel + antony afonso"
    )

    print(q)


