from json import JSONEncoder, JSONDecoder
from typing import NamedTuple, Dict

from . import set_default_encoder, set_default_decoder


class CoderPair(NamedTuple):
    encoder: JSONEncoder
    decoder: JSONDecoder


class CoderSwitch:
    def __init__(self, profile_name: str):
        self.coders = {}
        self.current_profile = profile_name

    def use(self, profile_name: str) -> None:
        encoder, decoder = self.coders[profile_name]
        set_default_encoder(encoder)
        set_default_decoder(decoder)
        self.current_profile = profile_name

    def register(self, profile_name: str, encoder: JSONEncoder, decoder: JSONDecoder) -> None:
        self.coders[profile_name] = CoderPair(encoder, decoder)

    def get_coder(self, profile_name: str) -> CoderPair:
        return self.coders[profile_name]

    def get_all_coders(self) -> Dict[str, CoderPair]:
        return self.coders

    def get_current_coder(self) -> CoderPair:
        return self.get_coder(self.current_profile)
