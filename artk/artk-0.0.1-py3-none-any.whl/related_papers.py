from urllib import response
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import csv
from scrapy import Selector
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import colored
from colored import stylize
import pyfiglet
from alive_progress import alive_bar
import os
import warnings
warnings.filterwarnings('ignore')

def get_titles(link):
    chromeOptions = Options()
    chromeOptions.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options = chromeOptions)
    driver.maximize_window()

    #Opening the link
    driver.get(link)
    sleep(2)

    #Clicking on the slider just once
    slider = driver.find_element(By.CSS_SELECTOR,'span[class="slider"]')
    slider.click()
    sleep(5)
    response = Selector(text=driver.page_source)

    #Scraping the titles
    titles = response.css("a.notinfluential.mathjax::text").extract()[0:3]
    try:
        title1 = titles[0].capitalize()
    except:
        title1 = ""
    try:
        title2 = titles[1].capitalize()
    except:
        title2 = ""
    try:
        title3 = titles[2].capitalize()
    except:
        title3 = ""
    titles = [title1, title2, title3]
    titles = list(filter(None, titles))
    return title1, title2, title3

def related_papers():
    link = input('\n Enter arXiv link:\n\n [https://arxiv.org/abs/XXXX.XXXXX] ')
    if 'abs' not in link:
        link = input(' Invalid link, please ensure link is of format \'https://arxiv.org/abs/XXXX.XXXXX\'. Try again:\n\n ')
        if 'abs' not in link:
            print(' Invalid link. If you believe your link is correct, reach out to \'maamari@usc.edu\' and I will look into the issue further.')
            return

    print('\n Processing...\n')
    with alive_bar(bar=None, spinner='fishes', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
        title1, title2, title3 = get_titles(link)

    os.system('clear')
    print(stylize("\n{}".format(pyfiglet.figlet_format("Related Papers", font = "stampatello")),colored.attr("bold")+colored.fg('green')))

    print(" Papers closely related to", link)
    print("  1: ", title1)
    print("  2: ", title2)
    print("  3: ", title3)
    
    input(stylize("\n Press Enter to continue...",colored.fg("green")))

    driver.close()
    driver.quit()


if __name__=='__main__':
    related_papers()
