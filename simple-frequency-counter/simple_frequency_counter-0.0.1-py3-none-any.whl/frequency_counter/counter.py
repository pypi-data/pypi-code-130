from pathlib import Path
import re

class FrequenciesGenerator:
    def __init__(self, source_folder):
        self.source_folder = source_folder 
        self.file_frequencies = {}  
        self.total_frequencies = {}  
        self.read_folder()
        
    def tokenize(self, text):
        return re.split(r'[\s.?,\-!)(:«»’"]+', text)

    def generate_frequencies(self, word_list):
        word_frequencies = {}
        for i in word_list:
            if i in word_frequencies:
                word_frequencies[i] += 1
            else:
                word_frequencies[i] = 1
        return word_frequencies

    def read_folder(self):
        files = Path(self.source_folder)
        for file in files.iterdir():

            if file.name.endswith('.txt'):
                with open(file, 'r', encoding="utf8") as reader:
                    read_file = reader.read()
                    tokenized_text = self.tokenize(read_file)

                    self.file_frequencies[file.name] = self.generate_frequencies(tokenized_text)
            else:
                raise ValueError('Only .txt file format is acceptable')

        self.total_frequencies = self.adding_dictionaries()
        return self.total_frequencies  

    def adding_dictionaries(self):

        value_list = self.file_frequencies.values() 

        for dictionary in value_list:
            for key, value in dictionary.items():
                if key in self.total_frequencies:
                    self.total_frequencies[key] += value
                else:
                    self.total_frequencies[key] = value
        return self.total_frequencies


    def get_frequency(self, token, file_name='default'):

        if 'default' != file_name:
            if file_name in self.file_frequencies:
                file_words = self.file_frequencies.get(file_name)
                if token in file_words:
                    print (f' the word {token} appears {file_words[token]} times in {file_name}') 
                else:
                    print (f' word {token} not found in {file_name}')
            else:
                print (f'{file_name} was not found')
        else:
            if token in self.total_frequencies:
                print (f'the word {token} appears {self.total_frequencies[token]} times in total')
            else:
                print (f'the word {token} appears 0 times in total')


    def calculate_similarity(self, file_a, file_b):

        common_tokens = set()

        try:
            file_a_dict = self.file_frequencies.get(file_a)
            file_b_dict = self.file_frequencies.get(file_b)
            file_a_tokens = file_a_dict.keys()
            file_b_tokens = file_b_dict.keys()

            for token in file_a_tokens:
                if token in file_b_tokens:
                    common_tokens.add(token)
            file_similarity = len(common_tokens) / (len(file_a_tokens) + len(file_b_tokens))

            print (f' {file_a} and {file_b} are {file_similarity * 100} % the same')
        except AttributeError:
            print ('non valid file names')
        