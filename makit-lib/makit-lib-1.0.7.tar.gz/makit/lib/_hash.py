#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liang20201101@163.com
@desc: 来自django并做了少量修改
"""
import base64
import hashlib
import importlib
import secrets
import math
import random

from makit.lib.encoding import encode

RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

_handlers = {}


class PasswordHandler:
    """
    加密处理器
    """
    algorithm = None
    library = None
    salt_entropy = 128

    def __init_subclass__(cls, **kwargs):
        _handlers[cls.algorithm] = cls
        return cls

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError as e:
                raise ValueError("Couldn't load %r algorithm library: %s" %
                                 (self.__class__.__name__, e))
            return module
        raise ValueError("Hasher %r doesn't specify a library attribute" %
                         self.__class__.__name__)

    def make_salt(self):
        char_count = math.ceil(self.salt_entropy / math.log2(len(RANDOM_STRING_CHARS)))
        return ''.join(random.choices(RANDOM_STRING_CHARS, k=char_count))

    def encode(self, text, salt):
        raise NotImplementedError

    def decode(self, hashed_text):
        raise NotImplementedError

    def verify(self, text, encoded_text):
        raise NotImplementedError


class PBKDF2PasswordHandler(PasswordHandler):
    algorithm = "pbkdf2_sha256"
    iterations = 260000
    digest = hashlib.sha256

    @classmethod
    def pbkdf2(cls, password, salt, iterations, dklen=0, digest=None):
        """Return the hash of password using pbkdf2."""
        if digest is None:
            digest = hashlib.sha256
        dklen = dklen or None
        password = encode(password)
        salt = encode(salt)
        return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dklen)

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hashed = self.pbkdf2(password, salt, iterations, digest=self.digest)
        hashed = base64.b64encode(hashed).decode('ascii').strip()
        return f"{self.algorithm}${iterations}${salt}${hashed}"

    def decode(self, encoded):
        algorithm, iterations, salt, hashed = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'hash': hashed,
            'iterations': int(iterations),
            'salt': salt,
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded2 = self.encode(password, decoded['salt'], decoded['iterations'])
        return secrets.compare_digest(encode(encoded), encode(encoded2))


class PBKDF2SHA1PasswordHandler(PBKDF2PasswordHandler):
    """
    Alternate PBKDF2 hasher which uses SHA1, the default PRF
    recommended by PKCS #5. This is compatible with other
    implementations of PBKDF2, such as openssl's
    PKCS5_PBKDF2_HMAC_SHA1().
    """
    algorithm = "pbkdf2_sha1"
    digest = hashlib.sha1


class Algorithm:
    PBKDF2_SHA256 = 'pbkdf2_sha256'
    PBKDF2_SHA1 = 'pbkdf2_sha1'


class Encryptor:
    def __init__(self):
        self._handlers = {}

    def get_handler(self, algorithm) -> 'PasswordHandler':
        handler = self._handlers.get(algorithm)
        if not handler:
            handler_cls = _handlers.get(algorithm)
            if not handler_cls:
                raise UnknownPasswordHandler(f'Unknown password handler for algorithm: {algorithm}')
            handler = handler_cls()
            self._handlers[algorithm] = handler
            return handler
        return handler

    def hash_password(self, password, salt=None, algorithm='pbkdf2_sha256'):
        assert password, 'Password to be hashed must not be empty!'
        if not isinstance(password, (bytes, str)):
            raise TypeError(f'Password must be a string or bytes, got {type(password).__qualname__}.')
        handler = self.get_handler(algorithm)
        salt = salt or handler.make_salt()
        return handler.encode(password, salt)

    def check_password(self, password, hashed_password):
        if password is None:
            return False
        algorithm = hashed_password.split('$', 1)[0]
        handler = self.get_handler(algorithm)
        return handler.verify(password, hashed_password)


class UnsupportedAlgorithmError(Exception):
    """"""


class UnknownPasswordHandler(Exception):
    """"""
