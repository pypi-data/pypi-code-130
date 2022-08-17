from w.services.abstract_service import AbstractService
from django.utils.crypto import get_random_string


class KeyGeneratorService(AbstractService):
    secret_key_length = 32
    prefix_length = 8

    @classmethod
    def _concatenate(cls, left: str, right: str) -> str:
        return "{}.{}".format(left, right)

    @classmethod
    def generate_secret_key(cls) -> str:
        prefix = get_random_string(cls.prefix_length)
        key = get_random_string(cls.secret_key_length)
        return cls._concatenate(prefix, key)
