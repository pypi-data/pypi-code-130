from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from jwt_smithy.file_saver import FileSaver


def _gen_private_key() -> EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def save_ecdsa_keys(directory: str):
    private_key = _gen_private_key()
    public_key = private_key.public_key()
    FileSaver(directory).save_key_pair(private_key, public_key)
