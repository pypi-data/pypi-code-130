import requests as rq
from bs4 import BeautifulSoup


def get_all_links(url):
    if ("https" or "http") in url:
        data = rq.get(url)
    else:
        data = rq.get("https://" + url)
    soup = BeautifulSoup(data.text, "html.parser")
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))

    return links[:20]