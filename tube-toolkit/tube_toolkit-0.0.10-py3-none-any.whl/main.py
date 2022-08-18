'''
  Copyright (C) 2022 TUBE
  This program is private software: you can't redistribute it and/or modify
  it without the agreement of the author.
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class Tube(object):
  def __init__(self, headless=True, developer_mode=False):
    '''
      developer_mode is for debugging purposes.
      headless is for running the program without a GUI.

      --headless is for running the browser in a headless mode.

      default args:
        --disable-extensions                          -> disable extensions (e.g. adblock, etc.) 
        --no-first-run                                -> Skip First Run tasks (e.g. default browser, etc.)
        --window-size=1920,1080                       -> set the window size
        --user-agent=Mozilla/5.0                      -> Set the user agent to a common one.
          (Windows NT 10.0; Win64; x64)
          AppleWebKit/537.36 (KHTML, like Gecko)
          Chrome/70.0.3538.77 Safari/537.36
    '''

    chrome_options = Options()
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--window-size=1920,1080')

    if headless == True:
      chrome_options.add_argument('--headless')

    if developer_mode == True:
      chrome_options.add_experimental_option("detach", True)

    self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)