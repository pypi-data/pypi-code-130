from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from jwt_smithy.file_saver import FileSaver


def _gen_private_key() -> RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )


def save_rsa_keys(directory: str):
    private_key = _gen_private_key()
    public_key = private_key.public_key()
    FileSaver(directory).save_key_pair(private_key, public_key)
