import random
import string


def password_gen():
    store = []
    char_length = random.randrange(2, 5)
    for char in range(char_length):
        upp = random.choices(string.ascii_uppercase)
        store += upp

        low = random.choices(string.ascii_lowercase)
        store += low

        punct = random.choices(string.punctuation)
        store += punct

        dig = random.choices(string.digits)
        store += dig

        random.shuffle(store)
        random.shuffle(store)

        word = "".join(store)

    return word


print(password_gen())
