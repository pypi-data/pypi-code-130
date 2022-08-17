from setuptools import setup, find_packages
import os



VERSION = '0.0.1'
DESCRIPTION = 'A simple python package to scrape useful data from Lectio.dk'
LONG_DESCRIPTION = 'A simple python package to scrape useful data off of the danish school system website Lectio (www.lectio.dk). Lectio doesn\'t have an official API, so this is just a good alternative to scraping the website directly.\n\nThis package is a work in progress and is not yet ready for use. It will be updated and maintained as needed.'

# Setting up
setup(
    name="lectioscraper",
    version=VERSION,
    author="Tovborg (Emil Tovborg-Jensen)",
    author_email="<emil@tovborg-jensen.dk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['beautifulsoup4', 'requests', 'lxml', 'pytz'],
    keywords=['python', 'Lectio', 'Scraping', 'webscraping'],

)