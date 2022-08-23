from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from pydwanimes.application.helper import get_player_class
from .player import Player


class Site(ABC):

    def __init__(self, player_config: Dict = None) -> None:
        if not player_config:
            player_config = {
                "directory": "static/animes",
            }
        self.player_config = player_config

    def import_player(self, player_name: str) -> Player:
        p = get_player_class(player_name, **self.player_config)
        return p

    @abstractmethod
    def search(self, slug: str) -> str:
        """ Search method get slug anime in anime site """
        pass

    @abstractmethod
    def get_multimedia_players(self, slug: str, chapter: int) -> List[str]:
        """" Return a list of available players """
        pass

    @abstractmethod
    def get_multimedia_url(self, slug: str, chapter: int) -> Tuple[str, str]:
        """ Return a tuple of multimedia_url and player_name """
        pass

    def download_multimedia(self, slug: str, chapter: int) -> None:
        """ Download and save video """
        print("Searching anime ... ")
        anime_slug = self.search(slug)
        print(f"{anime_slug} -- Anime found !")
        (url, player_name) = self.get_multimedia_url(anime_slug, chapter)

        player = self.import_player(player_name)
        player.download(url, f"cap-{chapter}")
