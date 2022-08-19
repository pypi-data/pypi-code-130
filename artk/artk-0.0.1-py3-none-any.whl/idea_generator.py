import sys
import scipdf
import openai
import signal
from artk.related_papers import get_titles
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from alive_progress import alive_bar
from simple_term_menu import TerminalMenu
import openai
import colored
from colored import stylize
import warnings
import pyfiglet
from artk.transform import transform
import os
import time
from datetime import datetime
warnings.filterwarnings("ignore")
from artk.parser import extract_text
# Set up dicts for summaries


future = []

def handler(signum, frame):
    exit(1)

def scrape(domain):
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=option)

    date = datetime(datetime.today().year, datetime.today().month-1, datetime.today().day).strftime('%Y-%m-%d')
    driver.get("https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term=&terms-0-field=title&classification-physics=y&classification-physics_archives={}&classification-include_cross_list=include&date-year=&date-filter_by=date_range&date-from_date={}&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=announced_date_first".format(domain,date))
    elem = driver.find_elements(By.XPATH, "//a[contains(text(),'pdf')]")

    links = []
    for link in elem:
        links.append(link.get_attribute('href'))

    return links

def idea_generator():
    idea_menu_title = "\n Select a domain:\n"
    idea_menu_items = ["Astro [astro-ph]",
                       "Condensed matter [cond-matt]",
                       "High energy theory [hep-th]",
                       "Mathematics [math]",
                       "Computing [CoRR]",
                       "Quantitative biology [q-bio]",
                       "Quantitative finance [q-fin]",
                       "Statistics [stat]",
                       "Electrical engineering [eess]",
                       "Economics [econ]"]
    idea_menu_cursor = "> "
    idea_menu_cursor_style = ("fg_green", "bold")
    idea_menu_style = ("italics", "bg_purple")
    idea_menu_exit = False

    idea_menu = TerminalMenu(
        menu_entries=idea_menu_items,
        title=idea_menu_title,
        menu_cursor=idea_menu_cursor,
        menu_cursor_style=idea_menu_cursor_style,
        menu_highlight_style=idea_menu_style,
        cycle_cursor=True
    )

    idea_sel = idea_menu.show()

    if idea_sel == 0:
        print('\n The Idea Generator is still in development. The process is inefficient and imperfect in many ways.\n Let this run in the background for 5 minutes and check back. No need to watch paint dry.\n To stop at any point, press Ctrl+c.')
        time.sleep(2)
        with alive_bar(title=' Finding recent articles...', bar=None, spinner='fishes', spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False): 
            links = scrape("astro-ph")

        signal.signal(signal.SIGINT, handler)
        for i, link in enumerate(links):
            print('\n')
            if (i%3==0) and (i>2): spinner = "fish"
            elif (i%2==0) and (i>1): spinner = "fishes"
            else: spinner = "fish2"  
            with alive_bar(title=' Processing...', bar=None, spinner=spinner, spinner_length=40, stats=False, monitor=False, elapsed=False, monitor_end=False, elapsed_end=False, stats_end=False, receipt=False):
                article_dict = extract_text(link+".pdf")
                title1, title2, title3 = get_titles(link.replace('pdf','abs'))
            
            keys = ['future', 'further', 'we leave', 'follow-up']
            ideas = []
            for section in article_dict['sections']:
                for paragraph in section['text']:
                    for sentence in paragraph.split('. '):
                        for key in keys:
                            if key in sentence:
                                ideas.append(' '+sentence)

            if len(ideas):
                print(stylize(" Title: {}".format(article_dict['title']),colored.attr("bold")+colored.fg("green")))
                print(stylize("  Related paper 1: {}".format(title1),colored.attr("bold")+colored.fg("green")))
                print(stylize("  Related paper 2: {}".format(title2),colored.attr("bold")+colored.fg("green")))
                print(stylize("  Related paper 3: {}".format(title3),colored.attr("bold")+colored.fg("green")))
                for idea in ideas:
                    print(idea)
                feedback = input(stylize(' Were any viable ideas presented?\n [y/n] ',colored.attr('bold')+colored.fg('green')))
            
'''
# Get paper
print('parsing text')
article_dict = extract_text("https://arxiv.org/pdf/1811.05477.pdf")
print('done parsing')

# Summarize sections
keys = ['future', 'further', 'we leave', 'follow-up']
for section in tqdm(article_dict['sections']):
    for paragraph in section['text']:
        for sentence in paragraph.split('. '):
            for key in keys:
                if key in sentence:
                    print("\n", key, section['heading'], "\n", sentence)
'''
