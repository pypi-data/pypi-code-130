from kbbi_scraper import constants, meaning

from functools import cached_property
from bs4 import BeautifulSoup
import requests

class Word:
    def __init__(self, word):
        self.word = word
        self.url = f'{constants.WORD_DETAIL_URL}/{word}'

    def __str__(self):
        return self.word

    @cached_property
    def html_text(self):
        return requests.get(self.url).text
    
    @cached_property
    def soup(self):
        return BeautifulSoup(self.html_text, 'html.parser')
    
    @cached_property
    def definition(self):
        meaning_list = self.soup.find_all('p', attrs={'class': 'arti'})
        result = []

        for m in meaning_list:
            mean = {}
            mean['symbols'] = constants.SYMBOL[m.find('i').text]

            if '--' in m.find('i').find_next_sibling('b').text:
                word = m.find('i').find_next_sibling('b')
                mean['word'] = word.text.replace('--', self.word).capitalize()
                mean['meaning'] = word.next_sibling.strip(' ').rstrip(';').capitalize()
                mean['meaning'] = mean['meaning'] if mean['meaning'].strip(',') else None
            else:
                mean['word'] = m.find('b').find('sup').next_sibling.replace('·', '').capitalize()
                mean['meaning'] = m.find('i').next_sibling.strip(' ').rstrip(';').capitalize()

            result.append(meaning.Meaning(**mean))

        return result
