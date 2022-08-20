import json
import os
from typing import Dict

import torch

from recanime.recommender.ranking_base_filter.model import FactorizationMachineModel


FM_MODEL_INPUT_DIR = os.getenv("FM_MODEL_INPUT_DIR", default='./model/ranking_base')


def get_fm_encoder_config() -> Dict:
    FM_MODEL_INPUT_DIR = './model/ranking_base'

    with open(FM_MODEL_INPUT_DIR + "/encode_config.json") as f:
        encoder_conig = json.load(f)

    return encoder_conig


def get_fm_model() -> FactorizationMachineModel:
    encoder_config = get_fm_encoder_config()
    user2user_encoded = encoder_config['user2user_encoded']
    anime2anime_encoded = encoder_config['anime2anime_encoded']

    n_users = len(user2user_encoded)
    n_animes = len(anime2anime_encoded)
    field_dims = [n_users, n_animes]

    model = FactorizationMachineModel(field_dims=field_dims, embed_dim=32)
    model.load_state_dict(
        torch.load(FM_MODEL_INPUT_DIR + "/model_state_dict.pt")
    )

    return model
