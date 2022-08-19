import string

class Tokenize:
    def __init__(self, code):
        print("Tokenize instance initialized..")
        self.lang = code

    def sentence_tokenize_mr(self, txt):
        punc_for_sentence_end = '''.!?'''
        sentences = []
        string = ""
        for i in txt:
            if i not in punc_for_sentence_end:
                string += i
            else:
                string += i
                sentences.append(string)
                string = ""
        print(sentences)
        
    def sentence_tokenize(self,txt):
        if (self.lang == 'mr'):
            self.sentence_tokenize_mr(txt)

    def word_tokenize_mr(self, txt):
        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for ele in txt:
            if ele in punc:
                txt = txt.replace(ele, "")
        x = txt.split()
        print(x)
        
    def word_tokenize(self,line):
        if (self.lang == 'mr'):
            self.word_tokenize_mr(line)


