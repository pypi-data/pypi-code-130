from UzMorphAnalyser import UzMorphAnalyser
import re
import pandas as pd
# from nltk.tokenize import word_tokenize

class Tagger:
    def __word_tokenize(self, text: str):
        # tokens = word_tokenize(text.replace('-', ' - '))
        tokens = re.findall(r'["!;:.,?-]|\w+', text)
        return tokens

    def pos_tag(self, text: str):
        tagged_text = []  # list of tuple [("men","PRN"), ("va", "CNJ")]
        # 0. text cleaning
        text = self.__text_cleaning(text)
        # 1. tokenize to words
        tokens = self.__word_tokenize(text)
        # print(tokens)

        # 2. read data
        df_non_aff = pd.read_csv('non_affixed_word.csv')

        df_lexicon = pd.read_csv('lexicon.csv')
        df_lexicon = df_lexicon.sort_values(by="stem", key=lambda x: x.str.len())  # sorting to stands a small one at top, after that get first item as a result

        uzmorph = UzMorphAnalyser.UzMorphAnalyser()

        punctuation = {'.', ',', '!', '?', ':'}  # punctuation list, set pos tag as "PUNC"
        symbol = {'$', '*', '#', '@', '%'}  # symbol list, set pos tag as "SYM"

        for token in tokens:
            # 3. check from ready list
            # 3.1 check from punctuation list
            if token in punctuation:
                tagged_text.append((token, self.POS.PUNC))  # punctuation
                continue
            # 3.1 check from symbol list
            if token in symbol:
                tagged_text.append((token, self.POS.SYM))  # symbol
                continue
            # 4. non_affixed_words check
            df1 = df_non_aff.loc[df_non_aff['stem'] == token.lower()]
            if not df1.empty:
                tagged_text.append((token, df1["pos"].iloc[0]))  # "non_aff"
                continue
            # 5. lookup from lexicon.csv, in reverse order by remove character
            df1 = df_lexicon[df_lexicon['stem'].str.startswith(token.lower())]
            if not df1.empty:
                tagged_text.append((token, df1["pos"].iloc[0]))  # "lexicon"
                continue
            # 6. UzMorph check
            res = uzmorph.analyze(token)
            if res[0]["pos"] != None:
                tagged_text.append((token, res[0]["pos"]))  # "uzmorph"
                continue
            # 7. still can not find, make any decision
            tagged_text.append((token, self.POS.NOUN))  # other

        return tagged_text

    class POS:
        NOUN = "NOUN"  # Noun
        VERB = "VERB"  # Verb
        ADJ = "ADJ"    # Adjective
        NUM = "NUM"    # Numeric
        ADV = "ADV"    # Adverb
        PRN = "PRN"    # Pronoun
        PUNC = "PUNC"  # Punctuation
        SYM = "SYM"    # Symbol

    def help(self):
        return "help of usage of metoding"

    def pos_tag_list(self):
        return [
            ('NOUN', 'Noun', 'Ot'),
            ('ADJ', 'Adjective', 'Sifat'),
            ('NUM', 'Number', 'Son'),
            ('PRON', 'Pronoun', 'Olmosh'),
            ('ADV', 'Adverb', 'Ravish'),
            ('VERB', 'Verb', 'Fel'),

            ('CNJ', 'Conjuction', 'Bog`lovchi'),
            ('ADP', 'Adposition', 'Ko`makchi'),
            ('PRT', 'Particle', 'Yuklama'),

            ('INTJ', 'Interjection', 'Undov'),
            ('MOD', 'Modal', 'Modal'),
            ('IMIT', 'Imitation', 'Taqlid'),

            ('AUX', 'Auxilary verb', 'Yodamchi fel'),
            ('PPN', 'Proper Noun', 'Atoqli ot'),
            ('PUNC', 'Punctuation', 'Tinish belgi'),
            ('SYM', 'Symbol', 'Belgi')
        ]

    def __text_cleaning(self, text: str):
        text = text.replace("g'", "g‘")
        text = text.replace("o'", "o‘")
        text = text.replace("g`", "g‘")
        text = text.replace("o`", "o‘")
        text = text.replace("g’", "g‘")
        text = text.replace("o’", "o‘")
        text = text.replace("gʻ", "g‘")
        text = text.replace("oʻ", "o‘")

        text = text.replace("G'", "G‘")
        text = text.replace("O'", "O‘")
        text = text.replace("G`", "G‘")
        text = text.replace("O`", "O‘")
        text = text.replace("G’", "G‘")
        text = text.replace("O’", "O‘")
        text = text.replace("Gʻ", "G‘")
        text = text.replace("Oʻ", "O‘")

        text = text.replace("'", "’")  # boshqa belgilarni ъ ni kodiga utirish
        text = text.replace("ʼ", "’")  # boshqa belgilarni ъ ni kodiga utirish
        text = text.replace("’", "’")  # boshqa belgilarni ъ ni kodiga utirish
        return text


# Tokenization
# Lower case conversion
# Stop Words removal
# Stemming
# Lemmatization
# Parse tree or Syntax Tree generation
# POS Tagging

# text = "Men va bollar 25-sanada parkka bormoqchimiz."
# obj = Tagger()
# res = obj.pos_tag(text)
# print(res)