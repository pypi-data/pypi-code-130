from abc import ABC, abstractmethod
from typing import Dict
from .player import Player


class Site(ABC):

    def __init__(self, player: Player) -> None:
        self.player = player

    @property
    def player_name(self) -> str:
        return self.player.__class__.__name__.lower()

    @abstractmethod
    def get_multimedia_url(self, slug, chapter) -> str:
        pass

    def download_multimedia(self, slug: str, chapter: int) -> None:
        """ Download and save video """
        url = self.get_multimedia_url(slug, chapter)
        self.player.download(url, f"cap-{chapter}")
