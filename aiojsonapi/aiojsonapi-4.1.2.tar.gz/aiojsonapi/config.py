"""Module with API configuration."""

import json
import typing


class Config:
    """API configuration."""

    def __init__(self):
        self.json_encoder = json.JSONEncoder
        self.json_decoder = json.JSONDecoder

    def set_json_encoder(self, encoder: typing.Type[json.JSONEncoder]):
        """Sets JSON encoder."""

        self.json_encoder = encoder

    def set_json_decoder(self, decoder: typing.Type[json.JSONDecoder]):
        """Sets JSON decoder."""

        self.json_decoder = decoder


config = Config()
