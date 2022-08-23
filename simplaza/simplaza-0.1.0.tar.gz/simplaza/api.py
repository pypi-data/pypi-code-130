import requests
import urllib.parse
import magneturi

import webbrowser
from bs4 import BeautifulSoup

from rich.console import Console
from rich.table import Table

class manager:
    def __init__(self) -> None:
        self.base_url = "https://simplaza.org/"
        self.console = Console()
        self.ignored_articles = [
            "Master List",
            "Scenery Map",
            "ddownload.com Master List",
            "Frequently Asked Questions",
        ]

    def parse_article_info(self, article) -> dict:
        article_id = article["id"].partition("-")[2]  # Regex?

        article_tags = []

        for tag in article["class"]:
            if "category" in tag:
                article_tags.append(
                    tag.partition("category")[2].partition("-")[2]
                )  # Edit this using regex

        basics = article.find("a")

        article_link = basics["href"]
        article_name = basics["title"]

        return {
            "name": article_name,
            "id": article_id,
            "link": article_link,
            "tags": article_tags,
        }

    def remove_ignored_articles(self, articles):
        valid_articles = []

        for article in articles:
            if (
                article.find("a")["title"] not in self.ignored_articles
            ):  # Don't repeat code?
                valid_articles.append(article)

        return valid_articles

    def request_soup(self, link):
        try:
            return BeautifulSoup(requests.get(link).content, "html.parser")
        except requests.exceptions.Timeout:
            return "Timeout"
        except requests.exceptions.TooManyRedirects:
            return "Incorrect URL"
        except requests.exceptions.RequestException as RequestError:
            raise SystemExit(RequestError)
        except Exception as Bs4Eror:
            raise systemExit(Bs4Eror)

    def search(self, query) -> dict:
        rsoup = self.request_soup(self.base_url + "?s=" + query)

        results = []

        for article in self.remove_ignored_articles(rsoup.find_all("article")):
            results.append(self.parse_article_info(article))

        return results

    def output_table(self, query_results):
        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("Name")
        table.add_column("Id")
        table.add_column("Link")
        table.add_column("Tags")

        for result in query_results:
            table.add_row(
                result["name"], result["id"], result["link"], ",".join(result["tags"])
            )

        self.console.print(table)

    def match_id_to_link(self, query_results, article_id):
        for article in query_results:
            if article["id"] == article_id:
                return article["link"]

    def open_torrent(self, torrent_data):
        webbrowser.open(magneturi.from_torrent_data(torrent_data))

    def get_torrent_data(self, article_link):
        torrent_html = self.request_soup(article_link).find_all("iframe")[1]
        query_decoded = urllib.parse.unquote(torrent_html["src"])

        torrent_link = query_decoded.partition('href="')[2].partition('"')[0]

        torrent_data = requests.get(torrent_link, allow_redirects=True).content

        return torrent_data