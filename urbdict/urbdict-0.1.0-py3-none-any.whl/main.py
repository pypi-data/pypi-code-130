import requests
from bs4 import BeautifulSoup


def define(words):
    def _get_word(soup, url):
        return soup.find("a", attrs={"href": url}).text

    def _get_definition(soup):
        return soup.find("div", attrs={"class": "break-words meaning mb-4"}).text

    def _get_example(soup):
        for br in soup.find_all("br"):
            br.replace_with("\n")
        return soup.find("div", attrs={"class": "break-words example italic mb-4"}).text

    def _get_contributor(soup):
        return soup.find("div", attrs={"class": "contributor font-bold"}).text

    words = words.lower()
    words = words.replace(" ", "%20")
    r = requests.get(f"http://www.urbandictionary.com/define.php?term={words}")
    soup = BeautifulSoup(r.content, "lxml")
    current_url = r.url.replace("%20", "+")
    current_url = current_url[current_url.rfind("/") :]
    try:
        word = _get_word(soup, current_url)
        definition = _get_definition(soup)
        example = _get_example(soup)
        contributor = _get_contributor(soup)
        return {
            "word": word,
            "definition": definition,
            "example": example,
            "contributor": contributor,
            "url": r.url,
        }
    except AttributeError:
        raise ValueError("Word not found: ", r.url)
