from abc import ABC, abstractmethod
from typing import List

import numpy as np

from recanime.anime_store.base import AnimeStoreBase
from recanime.schema.predict import AnimeAttributes, PredictResults
from recanime.schema.user import ExistedUserAttributesVector


class AnimeRecBase(ABC):
    def __init__(
        self,
        existed_user_attributes_vector: ExistedUserAttributesVector,
    ) -> None:
        self.existed_user_attributes_vector = existed_user_attributes_vector
        self.user_attribute_dim = len(
            existed_user_attributes_vector.attribute_map_to_vector_position
        )
        self.user_id2user_id_idx = {
            x: i for i, x in enumerate(
                existed_user_attributes_vector.user_ids
            )
        }
        self.user_id_idx2user_id = {
            i: x for i, x in enumerate(
                existed_user_attributes_vector.user_ids
            )
        }
        self.user_feature_matrix = np.vstack(
            existed_user_attributes_vector.user_attributes_vector
        )

    async def map_to_existed_user(self, attributes: AnimeAttributes) -> int:
        """Get the user's latent factor by mapping the attributes from existed user."""
        input_latent_factor: np.ndarray = np.zeros((self.user_attribute_dim), dtype=float)
        for genre, score in attributes.dict(by_alias=True).items():
            input_latent_factor[
                self.existed_user_attributes_vector.attribute_map_to_vector_position[genre]
            ] = score

        most_similar_user_id = self.user_id_idx2user_id[
            np.argmax(np.inner(self.user_feature_matrix, input_latent_factor))
        ]

        return most_similar_user_id

    @abstractmethod
    async def predict(
        self,
        anime_store: AnimeStoreBase,
        attributes: AnimeAttributes,
        top_k: int
    ) -> List[PredictResults]:
        """Retrieve the recommendation by the given attributes."""

        raise NotImplementedError()
