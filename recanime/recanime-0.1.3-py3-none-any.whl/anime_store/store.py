from typing import List, Text

import numpy as np
import pandas as pd

from recanime.anime_store.base import AnimeStoreBase
from recanime.schema.predict import AnimeAttributes, AnimeInfo


class AnimeStore(AnimeStoreBase):
    def __init__(self, anime_infos: List[AnimeInfo]) -> None:
        self.anime_df = pd.DataFrame(
            [anime_info.dict() for anime_info in anime_infos]
        )

    async def filter_anime_ids_by_attributes(
        self,
        attributes: AnimeAttributes,
    ) -> List[Text]:
        """Implement the base class method."""

        attributes_dict = attributes.dict()
        key_to_pop = []
        for key, value in attributes_dict.items():
            if value <= 0:
                key_to_pop.append(key)
        for key in key_to_pop:
            attributes_dict.pop(key)

        selected_attributes = set(attributes_dict.keys())
        selected_animes_df = self.anime_df[['anime_id', 'genres']].copy(deep=True)
        selected_animes_df['genres'] = selected_animes_df['genres'].apply(
            lambda x: np.nan if len(selected_attributes & set(x)) == 0 else x
        )
        selected_animes_df.dropna(inplace=True)
        selected_animes_dict = selected_animes_df.to_dict(orient='list')
        selected_anime_ids = selected_animes_dict['anime_id']

        return selected_anime_ids

    async def get_anime_informations_by_anime_id(
        self, anime_ids: List[Text]
    ) -> List[AnimeInfo]:
        """Implement the base class method."""

        selected_animes_df = self.anime_df[
            self.anime_df["anime_id"].isin(anime_ids)
        ].copy(deep=True)
        selected_animes = selected_animes_df.to_dict(orient='records')

        return [AnimeInfo(**selected_anime) for selected_anime in selected_animes]
