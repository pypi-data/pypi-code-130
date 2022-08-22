import hashlib


class ApiSecretHash:
    @staticmethod
    def hash_api_secret(plain_text_api_secret: str) -> str:
        secret_hash = hashlib.sha256()
        secret_hash.update(plain_text_api_secret.encode('UTF-8'))
        secret_hash = secret_hash.hexdigest()
        return secret_hash
