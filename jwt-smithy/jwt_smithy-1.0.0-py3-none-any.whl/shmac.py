import secrets

from jwt_smithy.file_saver import FileSaver


def _gen_key() -> str:
    return secrets.token_hex(256)


def save_shmac_keys(directory: str):
    key = _gen_key()
    FileSaver(directory).save_key_text("private.txt", key)
