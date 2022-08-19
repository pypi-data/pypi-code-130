from kbbi_scraper import constants

from functools import cached_property
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--headless")

import chromedriver_autoinstaller

chromedriver_autoinstaller.install()  
driver = webdriver.Chrome(options=chrome_options)

class Word:
    def __init__(self, word):
        self.word = word
        self.url = f'{constants.SOURCE_URL}/{word}'
        self.driver = driver

    def __str__(self):
        return self.word
    
    @cached_property
    def soup(self):
        self.driver.get(self.url)
        try:
            element = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "content")))
            soup = BeautifulSoup(element.get_attribute('innerHTML'), 'html.parser')
            self.driver.close()
            return soup
        except TimeoutException:
            print("Failed to load web source")

    @cached_property
    def desc_section(self):
        return self.soup.find('div', {'id': 'desc'})

    @cached_property
    def d1_section(self):
        return self.soup.find('div', {'id': 'd1'})

    @cached_property
    def base_word(self):
        return ''.join(self.syllables)

    @cached_property
    def syllables(self):
        try:
            syllable = self.d1_section.find_next('span', {'class': 'per-suku'}).text.strip('/').strip('\\')
        except AttributeError:
            syllable = self.d1_section.find('b', {'class': 'highlight'}).text.strip('/').strip('\\')
        
        try:
            word_number = self.d1_section.find('b').find('sup').text
            return syllable.replace(word_number, '').split('·')
        except AttributeError:
            return syllable.split('·')

    @cached_property
    def definition(self):
        meaning = []
        for num in self.d1_section.find_all_next('b', {'class': 'num'}):
            # Cuma nomor yang ada di div d1 section, yang ada didalem div sub_17 skip
            if num.parent == self.d1_section:

                # Arti dari peribahasa jangan dibawa, itu untuk property peribahasa
                if num.find_previous('em', {'class': 'pb'}):
                    continue
    
                if num.text == "1":
                    category = constants.CATEGORY[self.d1_section.find_next('em', {'class': 'jk'}).text.lower()]
                    m = num.next_element.next_element
                else:
                    category = constants.CATEGORY[num.find_next('em', {'class': 'jk'}).text.lower()] or constants.CATEGORY[self.d1_section.find_next('em', {'class': 'jk'}).text.lower()]

                    # Check if word is in the same category as the previous word
                    if category == constants.CATEGORY[self.d1_section.find_next('em', {'class': 'jk'}).text.lower()]:
                        m = num.next_element.next_element
                    else:
                        m = num.find_next('em', {'class': 'jk'}).next_element.next_element

                m_formatted = m.text.strip().strip(';').strip(':').capitalize()
                    
                meaning.append({
                    'meaning': m_formatted,
                    'category': category,
                    'example': m.find_next('em').text.replace('--', m_formatted).strip().strip(';').capitalize() if m.text.strip().endswith(':') else None
                })
            
        if not len(meaning):
            meaning.append(
                {
                    'meaning': self.d1_section.find_next('em', {'class': 'jk'}).next_element.next_element.text.strip().strip(';').strip(':').capitalize(),
                    'category': constants.CATEGORY[self.d1_section.find_next('em', {'class': 'jk'}).text.lower()],
                    'example': None
                }
            )
        return meaning
    
    @cached_property
    def related_words(self):
        return self.d1_section
