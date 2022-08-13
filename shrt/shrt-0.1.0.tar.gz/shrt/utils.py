import random
import string

characters = string.ascii_letters + string.digits


def random_path(length: int = 8) -> str:
    return ''.join(random.choice(characters) for i in range(length))
