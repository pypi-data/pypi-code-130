from abc import ABC, abstractmethod
from typing import List, Text

from recanime.schema.predict import AnimeAttributes, AnimeInfo


class AnimeStoreBase(ABC):
    """Store the anime list with id and the informations."""
    @abstractmethod
    async def filter_anime_ids_by_attributes(
        self,
        attributes: AnimeAttributes,
        *args,
        **kwargs
    ) -> List[Text]:
        """Filter out the list of anime_ids by the given attributes."""

        raise NotImplementedError()

    @abstractmethod
    async def get_anime_informations_by_anime_id(
        self, anime_ids: List[Text]
    ) -> List[AnimeInfo]:
        """Get anime's informations by anime_id."""

        raise NotImplementedError()
