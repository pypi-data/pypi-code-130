# Made By CodeBoard
"""
Encryptor and Decryptor Module
"""
import ast
from random import sample
import string


class JCryptor:
    """
    :class:`JCryptor`

    Encrypt and Decrypt Text.

    - Can use own key
    - Can save generated Key
    - Can generate new key

    Note:
        if text that pass in this is not in key, it will stay the same
        in encryption, the same goes with decryption.
    """

    def __init__(self) -> None:
        self.generate_new_key()

    def generate_new_key(self):
        """
        Generate New Key

        Note: 
            All American Standard Code for Information Interchange(ASCII)
            will be added soon. UTF Format

        """
        _letters = list(string.ascii_letters)
        _numbers = [str(i) for i in range(10)]
        _special_chr = [i for i in "!@#$%^&*()_+-/}[]|\\~`.,:;\"'<>?"]
        _all_chr = _letters + _numbers + _special_chr
        # Set Small Character Key
        _key_s_chr = dict(zip(string.ascii_lowercase, sample(_all_chr, 26)))
        _all_chr = [i for i in _all_chr if i not in _key_s_chr.values()]
        # Set Big Character Key
        _key_b_chr = dict(zip(string.ascii_uppercase, sample(_all_chr, 26)))
        _all_chr = [i for i in _all_chr if i not in _key_b_chr.values()]
        # Set Number Character Key
        _key_ord = dict(zip(_numbers, sample(_all_chr, len(_numbers))))
        _all_chr = [i for i in _all_chr if i not in _key_ord.values()]
        # Set Special Character Key
        _key_spc = dict(zip(_special_chr, sample(_all_chr, len(_special_chr))))
        # Combine all key in one big key.
        self._key = {**_key_s_chr, **_key_b_chr, **_key_ord, **_key_spc}

    def check_duplicate(self, text) -> str:
        """
        Check if there is duplicate in Text.
        """
        for t in text:
            if text.count(t) > 1:
                return t

    def set_key(self, key):
        """
        Set key by using own dictionary.

        - Must be a dictionary
        """
        self._key = key

    def get_key(self) -> dict:
        """
        Get the current key.
        """
        return self._key

    def set_using_file(self, filename):
        """
        Set key using a file, filetext, etc.
        """
        with open(filename, "r") as f:
            # Convert to dictionary
            self._key = ast.literal_eval(str(f.read()))

    def save_key(self, filename):
        """
        Save Current in file
        """
        with open(filename, "w") as f:
            f.write(str(self._key))

    def encrypt_text(self, text: str) -> str:
        """
        Encrypt Text.

        Example:

            cryptor = :class:`JCryptor()`
            original = "Test"
            encrypt_text = :func:`cryptor.encrypt_text(original)`

            print(original)
            print(encrypt_text)

        >> Test
        >> &gUT
        """
        result = ""
        for t in str(text):
            adder = self._key.get(t) if self._key.get(t) is not None else t
            result += adder
        return result

    def decrypt_text(self, text: str) -> str:
        """
        Decrypt Text:

        Example:

            cryptor = :class:`JCryptor()`
            encrypt = "&gUT"
            decrypt_text = :func:`cryptor.decrypt_text(encrypt)`

            print(encrypt)
            print(decrypt_text)

        >> &gUT
        >> Test
        """
        result = ""
        all_key = list(self._key.keys())
        all_val = list(self._key.values())
        for t in str(text):
            try:
                result += all_key[all_val.index(t)]
            except ValueError:
                result += t
        return result
