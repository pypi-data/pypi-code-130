import secrets
import string
import random


def generate_random_string(string_length=None, words=1):
    gen_words = []
    for word in range(words):
        string_length = random.randint(2, 12) if string_length is None else string_length
        rando_word = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(string_length))
        gen_words.append(rando_word)
        string_length = None
    return ' '.join(gen_words)
