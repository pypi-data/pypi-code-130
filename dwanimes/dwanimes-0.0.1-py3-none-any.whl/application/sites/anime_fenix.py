import pydwanimes.domain.site as site
from urllib import parse
import requests

from bs4 import BeautifulSoup


class AnimeFenix(site.Site):

    base_url = "https://www.animefenix.com"

    dictionary = {
        "yourupload": "YourUpload",
        "fireload": "Fireload",
        "fembed": "Fembed"
    }

    def get_tab_id(self, html: str, player_name: str) -> int:
        """ 
        Get tab id from attribute id='vid#ID' 

        Only supports : 
            -   YourUpload
        """
        soup = BeautifulSoup(html, "lxml")
        tab_id = soup.find("div", {
            "class": "tabs"
        }).find("ul").find("a", {
            "title": player_name
        })["href"].replace("#vid", "")

        return int(tab_id)

    def get_tab_url(self, html, i):
        """ 
            Get tab url only supports : 
            -   YourUpload
            -   Fireload
        """
        soup = BeautifulSoup(html, "lxml")
        s = soup.find("div", {
            "class": "player-container"
        }).find("script").string
        tabs = [tab.strip() for tab in s.strip().split("\n")]
        tabs.pop(0)
        tabs = [tab.split('"')[1] for tab in tabs]

        frames = []
        for tab in tabs:
            if not tab:
                continue
            f_soup = BeautifulSoup(tab, "lxml")
            f = f_soup.find("iframe")["src"]
            frames.append(f)

        return frames[i - 1]

    def get_embed_url(self, anime_slug: str, chapter: int) -> str:
        """ 
        Get embed url

        Parameters
        ----------
        anime_slug  (int)   example: overlord
        chapter     (int)   example: 1
        """

        url = self.base_url + f"/ver/{anime_slug}-{chapter}"
        req = requests.get(url)
        html = req.text

        tab_id = self.get_tab_id(html, self.dictionary[self.player_name])
        tab_url = self.get_tab_url(html, tab_id)

        return tab_url

    def get_code_of_embed(self, embed_url: str) -> str:
        parsed_url = parse.urlsplit(embed_url)
        qs = dict(parse.parse_qs(parsed_url.query))
        return qs["code"][0]

    def get_multimedia_url(self, slug, chapter) -> str:
        embed = self.get_embed_url(slug, chapter)
        print(f"EMBED URL -> {embed}")
        url = self.get_code_of_embed(embed)
        print(f"{self.player_name} VIDEO ID {url}")
        return url
