import os
import re
import json
import emoji
import string

class SentenceTokenizer:
    def __init__(self, keep_registry_punctuation = False):
        self.__set_regex()
        self.__set_word_vocab_dicts()
        self.__set_punctuation_to_keep()
        self.__set_all_letters()
        self.__set_all_valid_characters()
        if keep_registry_punctuation:
            self.__set_keep_registry_punctuation()
            self.remove_symbols = self.remove_symbols_keeping_registry
        else:
            self.remove_symbols = self.remove_symbols_not_keeping_registry
        self.removal_registry_lst = []
    
    def __set_regex(self):
        self.LAUGH_REGEX = re.compile(r'^((kk+)|(hah[ha]+)|(heh[he]+)|(hih[hi]+)|(rsr[rs]+))$')
        self.DATE_REGEX = re.compile(r'^(\d{1,2}[-//]\d{1,2})([-//]\d{2,4})?$')
        self.TIME_REGEX = re.compile(r'^\d{1,2}(:|h(rs)?)(\d{1,2}(min)?)?$')
        self.DDD_REGEX = re.compile(r'^(\(0?\d{2}\))$')
        self.MEASURE_REGEX = re.compile(r'^\d+[a-z]{1,2}$')
        self.CODE_REGEX = re.compile(r'^((\d+[a-z])|([a-z]+\d))\w*$')
        self.PHONE_REGEX = re.compile(r'^(\(0?\d{2}\))?\d{4,5}-?\d{4}$')
        self.CNPJ_REGEX = re.compile(r'^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$')
        self.CPF_REGEX = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$') 
        self.EMAIL_REGEX = re.compile(r'^\w+@\w+\.\w+(\.br)?$')
        self.MONEY_REGEX = re.compile(r'((([rR]?\$)|([rR][S$]?))(((\d{1,3}(\.\d{3})*(,\d{2})?))|(\d)+))$')
        self.URL_REGEX = re.compile(r'^((https?:\/\/)|(www\.))\w+\.\w+(\.\w+)*(\/.+)*$')
        self.NUMBER_REGEX =  re.compile(r'^[-+]?\d+([\.,-]\d+)*$')
        self.ORDINAL_NUMBER_REGEX = re.compile(r'^\d+[ºª]$')
        self.EMOJI_REGEX = re.compile('['
                                      u'\U0001f600-\U0001f64f'  # emoticons
                                      u'\U0001f300-\U0001f5ff'  # symbols & pictographs
                                      u'\U0001f680-\U0001f6ff'  # transport & map symbols
                                      u'\U0001f1e0-\U0001f1ff'  # flags (iOS)
                                                        ']+', flags=re.UNICODE)

        self.regex_lst = [self.EMOJI_REGEX, self.DATE_REGEX, self.TIME_REGEX, self.DDD_REGEX, self.PHONE_REGEX, self.CNPJ_REGEX, self.CPF_REGEX, self.EMAIL_REGEX,
                          self.MONEY_REGEX, self.URL_REGEX, self.LAUGH_REGEX, self.MEASURE_REGEX, self.ORDINAL_NUMBER_REGEX, self.NUMBER_REGEX, self.CODE_REGEX]
        self.COMBINED_REGEX = '|'.join(regex.pattern for regex in self.regex_lst)
        self.regex_dict = {self.EMOJI_REGEX: '',
                           self.DATE_REGEX: 'DATE',
                           self.TIME_REGEX: 'TIME',
                           self.DDD_REGEX: 'DDD',
                           self.PHONE_REGEX: 'PHONE',
                           self.CNPJ_REGEX: 'CNPJ',
                           self.CPF_REGEX: 'CPF',
                           self.EMAIL_REGEX: 'EMAIL',
                           self.MONEY_REGEX: 'MONEY',
                           self.URL_REGEX: 'URL',
                           self.LAUGH_REGEX: 'LAUGH',
                           self.MEASURE_REGEX: 'MEASURE',
                           self.ORDINAL_NUMBER_REGEX: 'NUMBER',
                           self.NUMBER_REGEX: 'NUMBER',
                           self.CODE_REGEX: 'CODE'}

    def __set_word_vocab_dicts(self):
        dir_path = os.path.dirname(__file__)
        full_path_correction = os.path.join(dir_path, 'dictionaries', 'correction_dict.json')
        full_path_accentuation = os.path.join(dir_path, 'dictionaries', 'Titan_v2_dict_without_accentuation.json')
        full_path_pt_words = os.path.join(dir_path, 'dictionaries', 'all_portuguese_words.txt')
        self.__correction_dict = self.__read_json(full_path_correction)
        self.__dict_without_accentuation = self.__read_json(full_path_accentuation)
        self.__set_pt_words = set(self.__read_txt_file(full_path_pt_words))

    def __set_punctuation_to_keep(self):
        self.punctuation_to_keep = {'!', ',', '.', ';', '?'}

    def __set_keep_registry_punctuation(self):
        discard_registry_set = set('\'"´^`~\\')
        self.keep_registry_punctuation = set(string.punctuation) - self.punctuation_to_keep - discard_registry_set
        self.keep_registry_punctuation.update(' ')
        
    def __set_all_letters(self):
        letters_set = set(string.ascii_letters)
        accented_letters = 'áéíóúàâêôãõç'
        uppercase_accented_letters = accented_letters.upper()
        accented_letters_set = set(accented_letters + uppercase_accented_letters)
        self.all_letters = letters_set.union(accented_letters_set)

    def __set_all_valid_characters(self):
        self.all_valid_characters = self.all_letters | self.punctuation_to_keep
        self.all_valid_characters.add(' ')

    def process_message(self, message: str):
        message_lst = message.split()
        if len(message_lst) < 1:
            return ''
        message_lst = self.lowercase_first_word(message_lst)
        message_lst = self.lowercase_caps_lock(message_lst)
        message_lst = self.add_space_punctuation(message_lst)
        message_lst = self.replace_words_in_sentence(message_lst)
        message_lst = self.replace_words_with_dicts(message_lst)
        message_lst = self.remove_whatsapp_emoji(message_lst)
        message_lst = self.lowercase_after_punctuation(message_lst)
        message = self.replace_symbol(' '.join(message_lst))
        message = self.split_punctuation(message)
        message_lst = self.replace_words_in_sentence(message.split())
        message_lst = self.replace_words_with_dicts(message_lst)
        message = self.remove_symbols(' '.join(message_lst))
        return message
    
    def __read_txt_file(self, txt_path: str):
        with open(txt_path, 'r',encoding='utf-8') as f:
            lines = [line.rstrip() for line in f]
            return lines
        
    def __read_json(self, dict_path: str):
        with open(dict_path, encoding='utf-8') as f:
            return json.loads(f.read())

    def lowercase_after_punctuation(self, message_lst: list):
        for ind, word in enumerate(message_lst[:-1]):
            if word in {'.', '!', '?'}:
                message_lst[ind + 1] = message_lst[ind+1].lower()
        return message_lst

    def replace_words_with_dicts(self, message_lst: list):
        for ind, word in enumerate(message_lst):
            if word in self.__correction_dict:
                message_lst[ind] = self.__correction_dict[word]
            elif (word in self.__dict_without_accentuation and word not in self.__set_pt_words):
                message_lst[ind] = self.__dict_without_accentuation[word]
        return message_lst
    
    def lowercase_first_word(self, message_lst: list):
        first_word = message_lst[0]
        if not first_word.isupper():
            message_lst[0] = first_word.lower()
        return message_lst

    def lowercase_caps_lock(self, message_lst: list):
        for ind, word in enumerate(message_lst):
            if word.isupper():
                message_lst[ind] = word.lower()
        return message_lst

    def add_space_punctuation(self, message_lst: list):
        processed_message_lst = []
        for word in message_lst:
            if len(word) > 1 and word[-1] in self.punctuation_to_keep:
                processed_message_lst += [word[:-1], word[-1]]
            else:
                processed_message_lst.append(word)
        return processed_message_lst
    
    def replace_words_in_sentence(self, message_lst: list):
        for ind, word in enumerate(message_lst):
            if re.match(self.COMBINED_REGEX, word):
                message_lst[ind] = self.__tag_word(word)
        return message_lst

    def remove_extra_spaces(self, message: str):
        return ' '.join(message.split())

    def split_punctuation(self, message: str):
        processed_message = ['x']
        for character in message: 
            last_valid_character = processed_message[-1]
            if (character in self.punctuation_to_keep and last_valid_character != ' ') or (last_valid_character in self.punctuation_to_keep and character != ' '):
                processed_message.append(' ')
            if character != ' ' or last_valid_character != ' ':
                processed_message.append(character)
        return ''.join(processed_message[1:])

    def remove_symbols_keeping_registry(self, message: str):
        message = self.remove_extra_spaces(message)
        processed_message = ['x']
        removal_registry_lst = [message]
        removed_registry_character = 0
        for character in message:
            last_valid_character = processed_message[-1]
            if character in self.all_valid_characters and (character != ' ' or last_valid_character != ' '):
                processed_message.append(character)
            else:
                removal_registry_lst.append({'punctuation': character, 'position': len(processed_message) + removed_registry_character - 1})
                removed_registry_character += 1
        if len(removal_registry_lst) > 1:
            self.removal_registry_lst.append(removal_registry_lst)
        return ''.join(processed_message[1:])

    def remove_symbols_not_keeping_registry(self, message: str):
        processed_message = [character for character in message if character in self.all_valid_characters]
        return self.remove_extra_spaces(''.join(processed_message))

    def remove_whatsapp_emoji(self, message_lst: list):
        message_lst[:] = [word for word in message_lst if word not in emoji.EMOJI_UNICODE.values()]
        return message_lst
    
    def __tag_word(self, word: str):
        for regex in self.regex_lst:
            processed_word, replacements = regex.subn(self.regex_dict[regex], word)
            if replacements > 0:
                return processed_word
    
    def replace_symbol(self, message: str):
        return (message
                .replace(';', ',')
                .replace('è', 'é')
                .replace('ì', 'í')
                .replace('ò', 'ó')
                .replace('ù', 'ú')
                .replace('ï', 'i')
                .replace('ü', 'u'))