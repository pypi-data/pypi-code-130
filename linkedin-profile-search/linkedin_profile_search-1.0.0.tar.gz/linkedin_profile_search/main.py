import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def replace_spaces(string):
    """
    It replaces all spaces in a string with periods
    
    :param string: The string to be modified
    :return: The string with all spaces replaced with periods.
    """
    return string.replace(" ", ".")

def word_in_string(word, string):
    return string.find(word) != -1

def split_string(sentence, pattern):
    return sentence.split(pattern)[0]

def profile_search(search, local=False, path=None, remote_url="http://54.36.177.119:4450",  credentials=None):
    """
    It takes a search term as an argument, opens a browser, goes to the quora search page, scrapes the
    usernames and urls of the results, and returns a dictionary with the usernames and urls
    
    :param search: The search term you want to search for
    :return: A dictionary of questions and their urls
    """
    
    # Checking if the credentials are None, if they are, it is assigning the default credentials to the
    # variable credentials.
    if credentials is None:
        credentials = {"email": "baahmedabdessamad@gmail.com", "password": "abdoabdo123"}
        
    try:
        # Opening a browser and going to the quora search page.
        # Creating a webdriver instance
        if local:
            driver = webdriver.Chrome(executable_path=path)
        else:
            chrome_options = webdriver.ChromeOptions()
            driver = webdriver.Remote(command_executor=remote_url, options=chrome_options)

        # Opening linkedIn's login page
        driver.get("https://linkedin.com/uas/login")

        # waiting for the page to load
        time.sleep(5)
        
        # entering username.
        username = driver.find_element(By.ID, "username")

        # Enter Your Email Address.
        username.send_keys(credentials["email"])  


        # entering password.
        pword = driver.find_element(By.ID, "password")

        # Enter Your Password.
        pword.send_keys(credentials["password"])


        # Clicking the "Sign in" button.
        driver.find_element(By.CLASS_NAME, "btn__primary--large.from__button--floating").click()

        time.sleep(5)

        url = f"https://www.linkedin.com/search/results/people/?keywords={search}&origin=GLOBAL_SEARCH_HEADER"
        driver.get(url)
        time.sleep(5)
        
        # Finding all the elements with the class name "app-aware-link"
        results = driver.find_elements(By.CLASS_NAME, "app-aware-link")

       # A list comprehension that is creating a list of users and urls.
        users = [split_string(result.text, "\n") for result in results if word_in_string("Profile", result.get_attribute("href")) and  word_in_string("Voir le profil", result.text)]
        urls = [result.get_attribute("href") for result in results if word_in_string("Profile", result.get_attribute("href")) and  word_in_string("Voir le profil", result.text)]
        
        # Creating a list of dictionaries with the usernames and urls.
        values = [{'username': user, 'url': url} for user, url in zip(users, urls)]
        profiles = [f"profile{str(index+1)}" for index, _ in enumerate(users)]

        # Closing the browser.
        driver.quit()
        
        return dict(zip(profiles, values)), users, urls
    
    except Exception as e:
        logging.error(f"Search on linkedin for {search} has failed")
        logging.error(e)
        driver.quit()

#print(profile_search(search="Elon Musk", local=True, path=r"C:\Users\KaisensData\Desktop\linkedin_crawler\chromedriver.exe"))