import logging
from typing import Dict, List

import torch
import pandas as pd

from recanime.anime_store.store import AnimeStore
from recanime.recommender.ranking_base_filter.model import FactorizationMachineModel
from recanime.recommender.base import AnimeRecBase
from recanime.schema.predict import AnimeAttributes, AnimeInfo, PredictResults
from recanime.schema.user import ExistedUserAttributesVector


logger = logging.getLogger(__name__)


class RankingBaseAnimeRec(AnimeRecBase):
    def __init__(
        self,
        existed_user_attributes_vector: ExistedUserAttributesVector,
        model: FactorizationMachineModel,
        model_encode_config: Dict,
    ) -> None:
        super().__init__(existed_user_attributes_vector)
        self.model = model
        self.model_user2user_encoded = model_encode_config['user2user_encoded']
        self.model_user_encoded2user = model_encode_config['user_encoded2user']
        self.model_anime2anime_encoded = model_encode_config['anime2anime_encoded']
        self.model_anime_encoded2anime = model_encode_config['anime_encoded2anime']

    async def predict(
        self,
        anime_store: AnimeStore,
        attributes: AnimeAttributes,
        top_k: int
    ) -> List[PredictResults]:
        """Implement the base class method."""

        self.model.eval()

        # Map to the most similar user from training data by given attributes.
        most_similar_user_id = await self.map_to_existed_user(
            attributes=attributes
        )
        most_similar_user_id_encoded = self.model_user2user_encoded[
            str(most_similar_user_id)
        ]

        # Select the anime which contains the attributes.
        selected_anime_ids = await anime_store.filter_anime_ids_by_attributes(
            attributes=attributes
        )
        selected_anime_ids_encoded = []
        anime_id_encoded_arg_2_anime_id = []
        for anime_id in selected_anime_ids:
            try:
                selected_anime_ids_encoded.append(
                    self.model_anime2anime_encoded[str(anime_id)]
                )
                anime_id_encoded_arg_2_anime_id.append(anime_id)
            except Exception as e:
                logger.debug(str(e))

        # Permute the user_id with anime_id to model's input format.
        user_id_encoded_with_selected_anime_ids_encoded = [
            [
                most_similar_user_id_encoded, anime_id_encoded
            ] for anime_id_encoded in selected_anime_ids_encoded
        ]
        user_id_encoded_with_selected_anime_ids_encoded_t = torch.tensor(
            user_id_encoded_with_selected_anime_ids_encoded
        )

        # Compute the most potential anime with the score which user likes.
        output: torch.Tensor = self.model(user_id_encoded_with_selected_anime_ids_encoded_t)
        output = output.squeeze()
        anime_scores, anime_ids_encoded_arg = output.sort(descending=True)
        k_anime_scores = anime_scores[:top_k].tolist()
        k_anime_ids_encoded_arg = anime_ids_encoded_arg[:top_k].tolist()
        k_anime_ids = []
        for anime_id_encode in k_anime_ids_encoded_arg:
            k_anime_ids.append(anime_id_encoded_arg_2_anime_id[anime_id_encode])

        # Convert to output format.
        k_anime_scores_df = pd.DataFrame({"anime_id": k_anime_ids, "predict_score": k_anime_scores})
        k_anime_infos = await anime_store.get_anime_informations_by_anime_id(
            k_anime_ids
        )
        k_anime_infos_df = pd.DataFrame(
            [k_anime_info.dict() for k_anime_info in k_anime_infos]
        )
        k_anime_info_with_scores_df = pd.merge(
            k_anime_scores_df,
            k_anime_infos_df,
            how="inner",
            on="anime_id"
        ).sort_values(by=["predict_score"], ascending=False)
        k_anime_info_with_scores = k_anime_info_with_scores_df.to_dict(
            orient='records'
        )

        predict_results: List[PredictResults] = []
        for anime_info_with_score in k_anime_info_with_scores:
            predict_score = anime_info_with_score.pop("predict_score")
            predict_results.append(
                PredictResults(
                    predict_score=predict_score,
                    anime_info=AnimeInfo(**anime_info_with_score)
                )
            )

        return predict_results
