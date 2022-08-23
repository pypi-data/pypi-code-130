# import Asclepius dependencies
from asclepius.instelling import GGZ, Instelling, ZKH
from asclepius.medewerker import Medewerker

# import other dependencies
from selenium import webdriver
from selenium.webdriver.common.by import By
from pandas import DataFrame, read_excel
from time import sleep
from re import compile, search

class PortaalDriver:
    driver = 'C:\Program Files (x86)\chromedriver.exe'
    
    def __init__(self, gebruiker: Medewerker, product: str, target_link: str = None, download_link: str = None, variabele_links: DataFrame = None):
        self.gebruiker = gebruiker
        self.driver = PortaalDriver.driver
        self.portaal = None

        self.product = product
        self.target_link = target_link
        self.download_link = download_link
        self.variabele_links = variabele_links
        return None

    def __str__(self) -> str:
        pass

    def __repr__(self) -> str:
        pass

    def webscraper(self, instelling: GGZ|Instelling|ZKH):
        """Download de relevante Excelsheets van de opgegeven instelling."""

        # set de juiste target en download links
        instelling.link_setter(self.target_link, self.download_link, self.variabele_links)

        # download excels uit acceptatie omgeving
        instelling.kies_omgeving('acceptatie')
        self.webscraper_portaal(instelling)

        # download excels uit productie omgeving
        instelling.kies_omgeving('productie')
        self.webscraper_portaal(instelling)
        return None

    def webscraper_portaal(self, instelling):
        # inloggen op het portaal
        self.inloggen(instelling)

        # download excel ZPM prestatiekaart
        self.download_excel(instelling)
        self.gebruiker.webscraper_hernoem_bestand(instelling, self.product)

        # sluit het portaal af
        self.portaal.close()
        return None
    
    def inloggen(self, instelling: GGZ|Instelling|ZKH):
        # open portaal
        self.portaal = webdriver.Chrome(self.driver)
        
        # haal de loginpagina op
        self.portaal.get(instelling.login)
        sleep(2)
        
        # vind invoer op de pagina
        username = self.portaal.find_element(By.NAME, 'username')
        password = self.portaal.find_element(By.NAME, 'password')
        submit = self.portaal.find_element(By.NAME, 'submit')
        
        # verstuur de informatie van de gebruiker
        username.send_keys(self.gebruiker.gebruikersnaam)
        password.send_keys(self.gebruiker.wachtwoord)
        submit.click()
        sleep(2)
        return

    def download_excel(self, instelling: GGZ|Instelling|ZKH):
        self.portaal.get(instelling.target_link)
        sleep(2)
        self.portaal.get(instelling.download_link)
        sleep(5)
        return None