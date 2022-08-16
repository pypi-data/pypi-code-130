from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

PRIVATE_KEY_TYPES = EllipticCurvePrivateKey | RSAPrivateKey
PUBLIC_KEY_TYPES = EllipticCurvePublicKey | RSAPublicKey
KEY_TYPES = PRIVATE_KEY_TYPES | PUBLIC_KEY_TYPES | str


class FileSaver:
    def __init__(self, directory: str):
        self.directory = directory

    def save_key_pair(
            self,
            private_key: PRIVATE_KEY_TYPES,
            public_key: PUBLIC_KEY_TYPES
    ):
        self.save_private_key("private.pem", private_key)
        self.save_public_key("public.pem", public_key)

    def save_private_key(
            self,
            key_name: str,
            key: PRIVATE_KEY_TYPES
    ):
        self.save_key(key_name, key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()))

    def save_public_key(
            self,
            key_name: str,
            key: PUBLIC_KEY_TYPES
    ):
        self.save_key(key_name, key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    def save_key(self, key_name: str, key: bytes):
        self._create_dir_if_not_exists()
        with open(Path(self.directory) / key_name, "wb") as f:
            f.write(key)

    def save_key_text(self, key_name: str, key: str):
        self._create_dir_if_not_exists()
        with open(Path(self.directory) / key_name, "w") as f:
            f.write(key)

    def _create_dir_if_not_exists(self):
        Path(self.directory).mkdir(parents=True, exist_ok=True)
