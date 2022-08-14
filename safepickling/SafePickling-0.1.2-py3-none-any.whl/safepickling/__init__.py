import pickle
import secrets

import hashlib
from hmac import compare_digest

from dataclasses import dataclass, field

@dataclass
class SafePickling():
    """
    A class to store keys and only encode/decode valid pickle objects

    Attributes:
        key: The key to use for signing and verification(set using set_key or generate_key methods)
        trusted_keys: A list of trusted keys to verify the signature(set using add_trusted_keys method)
        algorithm: The algorithm to use for signing and verification(can be either of the blake2 algorithms in the hashlib module, key length is automatically determined)
        personalization: The personalization to use for signing and verification(can be any bytes, gets passed to the hashing algorithm)

    Methods:
        set_key: Set the key for use by the client, check if key is MAX_KEY_SIZE
        generate_key: Generate a key for use by the client(Sets it automatically)
        add_trusted_keys: Add trusted keys to the list of trusted keys
        pickle: Pickle an object and sign it
        unpickle: Unpickle the object bytes only if the signature is in trusted keys
    
    """
    key: bytes = field(init=False)
    trusted_keys: list[bytes] = field(init=False, default_factory=list)
    algorithm = hashlib.blake2b
    personalization: bytes = b"SafePickling"

    def __is_valid_hash(self, obj_bytes: bytes) -> bool:
        """
        Check if the signature is in trusted keys
        """
        signature, pickled = obj_bytes[:self.algorithm.MAX_DIGEST_SIZE], obj_bytes[self.algorithm.MAX_DIGEST_SIZE:]
        for key in self.trusted_keys:
            if compare_digest(signature, self.algorithm(pickled, key=key, person=self.personalization).digest()):
                return True
            else:
                continue
        else:
            raise Exception("Signature not in trusted keys")

    def set_key(self, key: bytes):
        """
        Set the key for use by the client, check if key is MAX_KEY_SIZE
        """
        if len(key) == self.algorithm.MAX_KEY_SIZE:
            self.key = key
        else:
            raise Exception("Key is not the correct length")

    def generate_key(self) -> bytes:
        """
        Generate a key for use by the client(Sets it automatically)
        """
        self.key = secrets.token_bytes(self.algorithm.MAX_KEY_SIZE)
        return self.key

    def add_trusted_keys(self, keys: list[bytes]):
        """
        Add trusted keys to the list of trusted keys
        """
        self.trusted_keys.extend(keys)

    def pickle(self, obj: object) -> bytes:
        """
        Pickle an object and sign it
        """
        if not self.key:
            raise Exception("No key set")

        pickled = pickle.dumps(obj)
        signature = self.algorithm(pickled, key=self.key, person=self.personalization).digest()
        return signature + pickled

    def unpickle(self, obj_bytes: bytes) -> object:
        """
        Unpickle the object bytes only if the signature is in trusted keys
        """
        if not self.trusted_keys:
            raise Exception("No trusted keys")

        _, pickled = obj_bytes[:self.algorithm.MAX_DIGEST_SIZE], obj_bytes[self.algorithm.MAX_DIGEST_SIZE:]
        if self.__is_valid_hash(obj_bytes):
            return pickle.loads(pickled)
        else:
            raise Exception("Invalid signature")
