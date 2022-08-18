#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from zenutils import base64utils
from zenutils.sixutils import *

__all__ = [
    "method_load",
    "get_file_hash",
    "get_file_md5",
    "get_file_sha",
    "get_file_sha1",
    "get_file_sha224",
    "get_file_sha256",
    "get_file_sha384",
    "get_file_sha512",
    "get_hash_hexdigest",
    "get_md5",
    "get_sha",
    "get_sha1",
    "get_sha224",
    "get_sha256",
    "get_sha384",
    "get_sha512",
    "get_md5_hexdigest",
    "get_sha_hexdigest",
    "get_sha1_hexdigest",
    "get_sha224_hexdigest",
    "get_sha256_hexdigest",
    "get_sha384_hexdigest",
    "get_sha512_hexdigest",
    "get_hash_base64",
    "get_md5_base64",
    "get_sha_base64",
    "get_sha1_base64",
    "get_sha224_base64",
    "get_sha256_base64",
    "get_sha384_base64",
    "get_sha512_base64",
    "pbkdf2_hmac",
    "get_pbkdf2_hmac",
    "validate_pbkdf2_hmac",
    "get_pbkdf2_md5",
    "get_pbkdf2_sha",
    "get_pbkdf2_sha1",
    "get_pbkdf2_sha224",
    "get_pbkdf2_sha256",
    "get_pbkdf2_sha384",
    "get_pbkdf2_sha512",
    "validate_pbkdf2_md5",
    "validate_pbkdf2_sha",
    "validate_pbkdf2_sha1",
    "validate_pbkdf2_sha224",
    "validate_pbkdf2_sha256",
    "validate_pbkdf2_sha384",
    "validate_pbkdf2_sha512",
    "register_password_hash_method",
    "get_password_hash_methods",
    "get_password_hash",
    "validate_password_hash",
]

import re
import string
import hashlib
import functools

# ##################################################################################
# being: copy from hashlib of python3.9 to fix pbkdf2_hmac missing in python3.3/python3.2
# ##################################################################################
try:
    # OpenSSL's PKCS5_PBKDF2_HMAC requires OpenSSL 1.0+ with HMAC and SHA
    from hashlib import pbkdf2_hmac
except ImportError:
    _trans_5C = bytes((x ^ 0x5C) for x in range(256))
    _trans_36 = bytes((x ^ 0x36) for x in range(256))

    def pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None):
        """Password based key derivation function 2 (PKCS #5 v2.0)

        This Python implementations based on the hmac module about as fast
        as OpenSSL's PKCS5_PBKDF2_HMAC for short passwords and much faster
        for long passwords.
        """
        if not isinstance(hash_name, str):
            raise TypeError(hash_name)

        if not isinstance(password, (bytes, bytearray)):
            password = bytes(memoryview(password))
        if not isinstance(salt, (bytes, bytearray)):
            salt = bytes(memoryview(salt))

        # Fast inline HMAC implementation
        inner = hashlib.new(hash_name)
        outer = hashlib.new(hash_name)
        blocksize = getattr(inner, 'block_size', 64)
        if len(password) > blocksize:
            password = hashlib.new(hash_name, password).digest()
        password = password + b'\x00' * (blocksize - len(password))
        inner.update(password.translate(_trans_36))
        outer.update(password.translate(_trans_5C))

        def prf(msg, inner=inner, outer=outer):
            # PBKDF2_HMAC uses the password as key. We can re-use the same
            # digest objects and just update copies to skip initialization.
            icpy = inner.copy()
            ocpy = outer.copy()
            icpy.update(msg)
            ocpy.update(icpy.digest())
            return ocpy.digest()

        if iterations < 1:
            raise ValueError(iterations)
        if dklen is None:
            dklen = outer.digest_size
        if dklen < 1:
            raise ValueError(dklen)

        dkey = b''
        loop = 1
        from_bytes = int.from_bytes
        while len(dkey) < dklen:
            prev = prf(salt + loop.to_bytes(4, 'big'))
            # endianness doesn't matter here as long to / from use the same
            rkey = int.from_bytes(prev, 'big')
            for i in range(iterations - 1):
                prev = prf(prev)
                # rkey = rkey ^ prev
                rkey ^= from_bytes(prev, 'big')
            loop += 1
            dkey += rkey.to_bytes(inner.digest_size, 'big')

        return dkey[:dklen]

    hashlib.pbkdf2_hmac = pbkdf2_hmac
# ##################################################################################
# end: copy from hashlib of python3.9 to fix pbkdf2_hmac missing in python3.3/python3.2
# ##################################################################################

def method_load(method):
    """Get hash generator class by method name.

    @Returns:
        (hash generator class)
    
    @Parameters:
        method(str, bytes, hash generator class): Hash generator class name.
    """
    if isinstance(method, (BYTES_TYPE, STR_TYPE)):
        method = force_text(method)
        return getattr(hashlib, method)
    else:
        return method

def get_file_hash(filename, method, buffer_size=1024*64):
    method = method_load(method)
    gen = method()
    with open(filename, "rb") as fobj:
        while True:
            buffer = fobj.read(buffer_size)
            if not buffer:
                break
            gen.update(buffer)
    return gen.hexdigest()

get_file_md5 = functools.partial(get_file_hash, method=hashlib.md5)
get_file_sha = functools.partial(get_file_hash, method=hashlib.sha1)
get_file_sha1 = functools.partial(get_file_hash, method=hashlib.sha1)
get_file_sha224 = functools.partial(get_file_hash, method=hashlib.sha224)
get_file_sha256 = functools.partial(get_file_hash, method=hashlib.sha256)
get_file_sha384 = functools.partial(get_file_hash, method=hashlib.sha384)
get_file_sha512 = functools.partial(get_file_hash, method=hashlib.sha512)

def get_hash_hexdigest(*args, **kwargs):
    method = kwargs.get("method", "md5")
    gen_class = method_load(method)
    gen = gen_class()
    for arg in args:
        gen.update(force_bytes(arg))
    result = force_text(gen.hexdigest())
    return result

get_md5 = get_md5_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.md5)
get_sha = get_sha_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha1)
get_sha1 = get_sha1_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha1)
get_sha224 = get_sha224_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha224)
get_sha256 = get_sha256_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha256)
get_sha384 = get_sha384_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha384)
get_sha512 = get_sha512_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha512)

def get_hash_base64(*args, **kwargs):
    from zenutils import strutils
    from zenutils import base64utils
    method = kwargs.get("method", "md5")
    gen_class = method_load(method)
    gen = gen_class()
    for arg in args:
        gen.update(force_bytes(arg))
    data = gen.digest()
    result = force_text(base64utils.encodebytes(data))
    return strutils.join_lines(result)

get_md5_base64 = functools.partial(get_hash_base64, method=hashlib.md5)
get_sha_base64 = functools.partial(get_hash_base64, method=hashlib.sha1)
get_sha1_base64 = functools.partial(get_hash_base64, method=hashlib.sha1)
get_sha224_base64 = functools.partial(get_hash_base64, method=hashlib.sha224)
get_sha256_base64 = functools.partial(get_hash_base64, method=hashlib.sha256)
get_sha384_base64 = functools.partial(get_hash_base64, method=hashlib.sha384)
get_sha512_base64 = functools.partial(get_hash_base64, method=hashlib.sha512)

def get_salted_hash_base64(*args, **kwargs):
    from zenutils import strutils
    from zenutils import base64utils
    method = kwargs.get("method", "md5")
    salt_length = kwargs.get("salt_length", 4)
    salt = kwargs.get("salt", None)
    if salt is None:
        salt = strutils.random_string(length=salt_length)
    gen_class = method_load(method)
    gen = gen_class()
    for arg in args:
        gen.update(force_bytes(arg))
    gen.update(force_bytes(salt))
    data = gen.digest() + force_bytes(salt)
    result = force_text(base64utils.encodebytes(data))
    return strutils.join_lines(result)

get_salted_md5_base64 = functools.partial(get_hash_base64, method=hashlib.md5)
get_salted_sha_base64 = functools.partial(get_hash_base64, method=hashlib.sha1)
get_salted_sha1_base64 = functools.partial(get_hash_base64, method=hashlib.sha1)
get_salted_sha224_base64 = functools.partial(get_hash_base64, method=hashlib.sha224)
get_salted_sha256_base64 = functools.partial(get_hash_base64, method=hashlib.sha256)
get_salted_sha384_base64 = functools.partial(get_hash_base64, method=hashlib.sha384)
get_salted_sha512_base64 = functools.partial(get_hash_base64, method=hashlib.sha512)

def get_pbkdf2_hmac(text, salt=None, iterations=2048, hash_name="sha256", seperator_between_pbkdf2_and_method="_"):
    from zenutils import strutils
    from zenutils import base64utils

    if salt is None:
        salt = strutils.random_string(16, choices=string.ascii_letters)
    text = force_bytes(text)
    salt = force_bytes(salt)
    data = hashlib.pbkdf2_hmac(hash_name, text, salt, iterations)
    return "pbkdf2{seperator}{hash_name}${iterations}${salt}${data}".format(
        seperator=seperator_between_pbkdf2_and_method,
        hash_name=TEXT(hash_name),
        iterations=iterations,
        salt=TEXT(salt),
        data=strutils.join_lines(TEXT(base64utils.encodebytes(data))),
    )

def validate_pbkdf2_hmac(password, text):
    text = force_text(text)
    matches = re.findall("pbkdf2([_:])(.+)\\$(\\d+)\\$(.+)\\$(.+)", text)
    if len(matches) != 1:
        return False
    sep, hash_name, iterations, salt, _ = matches[0]
    if not iterations.isdigit():
        return False
    else:
        iterations = int(iterations)
    data = get_pbkdf2_hmac(password, salt=salt, iterations=iterations, hash_name=hash_name, seperator_between_pbkdf2_and_method=sep)
    if data == text:
        return True
    else:
        return False

get_pbkdf2_sha512 = functools.partial(get_pbkdf2_hmac, hash_name="sha512")
validate_pbkdf2_sha512 = validate_pbkdf2_hmac

get_pbkdf2_sha384 = functools.partial(get_pbkdf2_hmac, hash_name="sha384")
validate_pbkdf2_sha384 = validate_pbkdf2_hmac

get_pbkdf2_sha256 = functools.partial(get_pbkdf2_hmac, hash_name="sha256")
validate_pbkdf2_sha256 = validate_pbkdf2_hmac

get_pbkdf2_sha224 = functools.partial(get_pbkdf2_hmac, hash_name="sha224")
validate_pbkdf2_sha224 = validate_pbkdf2_hmac

get_pbkdf2_sha1 = functools.partial(get_pbkdf2_hmac, hash_name="sha1")
validate_pbkdf2_sha1 = validate_pbkdf2_hmac

get_pbkdf2_sha = functools.partial(get_pbkdf2_hmac, hash_name="sha1")
validate_pbkdf2_sha = validate_pbkdf2_hmac

get_pbkdf2_md5 = functools.partial(get_pbkdf2_hmac, hash_name="md5")
validate_pbkdf2_md5 = validate_pbkdf2_hmac

PASSWORD_HASH_METHODS = {}

class PasswordHashMethodNotSupportError(Exception):
    pass

def register_password_hash_method(name, password_hash_method_instance):
    PASSWORD_HASH_METHODS[name] = password_hash_method_instance

def get_password_hash_methods():
    methods = list(PASSWORD_HASH_METHODS.keys())
    methods.sort()
    return methods

def get_password_hash(password, method="SSHA"):
    """
    4 kind password hash format supported:

    1. Simple hash with method prefix. e.g. {SHA1}w0mcJylzCn+AfvuGdqkty2+KP48=
    2. Salted hash with method prefix. e.g. {SSHA}qWgORjfMmQJPipkl0KtdvQ6rGcppdVBIZGtGcQ==
    3. Pbkdf2 hmac hash. e.g. 'pbkdf2_sha256$2048$TdisEdeyNKNltWAj$eLzCMpQjSDIh9GFMjJCzhBPexrfeQfoLYypbHtTH6V8='
    4. Simple hash in hex digest. e.g. c3499c2729730a7f807efb8676a92dcb6f8a3f8f.
    """
    method = method.upper()
    password_hash_method = PASSWORD_HASH_METHODS.get(method, None)
    if password_hash_method:
        return password_hash_method.get_password_hash(password)
    else:
        raise PasswordHashMethodNotSupportError()

def validate_password_hash(password_hash_data, password):
    for _, method in PASSWORD_HASH_METHODS.items():
        result = method.validate_password_hash(password_hash_data, password)
        if result in [True, False]:
            return result
    raise PasswordHashMethodNotSupportError()

class PasswordHashMethodBase(object):

    def get_password_hash(self, password):
        pass

    def validate_password_hash(self, password_hash_data, password):
        pass

class Pbkdf2PasswordHashMethod(PasswordHashMethodBase):

    seperator_between_pbkdf2_and_method = "_"
    method = "sha1"
    prefix = "pbkdf2_sha1"

    def get_password_hash(self, password):
        return get_pbkdf2_hmac(password, hash_name=self.method, seperator_between_pbkdf2_and_method=self.seperator_between_pbkdf2_and_method)

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        return validate_pbkdf2_hmac(password, password_hash_data)

class Pbkdfs2Md5PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "md5"
    prefix = "pbkdf2_md5"

class Pbkdfs2Md5PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "md5"
    prefix = "pbkdf2:md5"

class Pbkdfs2ShaPasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha1"
    prefix = "pbkdf2_sha"

class Pbkdfs2ShaPasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha1"
    prefix = "pbkdf2:sha"

class Pbkdfs2Sha1PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha1"
    prefix = "pbkdf2_sha1"

class Pbkdfs2Sha1PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha1"
    prefix = "pbkdf2:sha1"

class Pbkdfs2Sha224PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha224"
    prefix = "pbkdf2_sha224"

class Pbkdfs2Sha224PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha224"
    prefix = "pbkdf2:sha224"

class Pbkdfs2Sha256PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha256"
    prefix = "pbkdf2_sha256"

class Pbkdfs2Sha256PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha256"
    prefix = "pbkdf2:sha256"

class Pbkdfs2Sha384PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha384"
    prefix = "pbkdf2_sha384"

class Pbkdfs2Sha384PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha384"
    prefix = "pbkdf2:sha384"

class Pbkdfs2Sha512PasswordHashMethod(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = "_"
    method = "sha512"
    prefix = "pbkdf2_sha512"

class Pbkdfs2Sha512PasswordHashMethodColon(Pbkdf2PasswordHashMethod):
    seperator_between_pbkdf2_and_method = ":"
    method = "sha512"
    prefix = "pbkdf2:sha512"

class SimplePasswordHashMethod(PasswordHashMethodBase):
    
    method = "sha1"
    prefix = "{SHA}"

    def get_password_hash(self, password):
        return self.prefix + get_hash_base64(password, method=self.method)

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        new_password_hash_data = self.get_password_hash(password)
        return new_password_hash_data == password_hash_data

class Md5PasswordHashMethod(SimplePasswordHashMethod):
    method = "md5"
    prefix = "{MD5}"

class ShaPasswordHashMethod(SimplePasswordHashMethod):
    method = "sha1"
    prefix = "{SHA}"

class Sha1PasswordHashMethod(SimplePasswordHashMethod):
    method = "sha1"
    prefix = "{SHA1}"

class Sha224PasswordHashMethod(SimplePasswordHashMethod):
    method = "sha224"
    prefix = "{SHA224}"

class Sha256PasswordHashMethod(SimplePasswordHashMethod):
    method = "sha256"
    prefix = "{SHA256}"

class Sha384PasswordHashMethod(SimplePasswordHashMethod):
    method = "sha384"
    prefix = "{SHA384}"

class Sha512PasswordHashMethod(SimplePasswordHashMethod):
    method = "sha512"
    prefix = "{SHA512}"

class SimpleSaltPasswordHashMethod(PasswordHashMethodBase):

    method = "sha1"
    prefix = "{SSHA}"
    salt_length = 8
    hash_size = 20

    def get_password_hash(self, password, salt_length=None, salt=None):
        if salt_length is None:
            salt_length = self.salt_length
        return self.prefix + get_salted_hash_base64(password, salt_length=salt_length, salt=salt, method=self.method)

    def validate_password_hash(self, password_hash_data, password):
        if not hasattr(self, "prefix"):
            return None
        if not password_hash_data.startswith(self.prefix):
            return None
        salt = base64utils.decodebytes(force_bytes(password_hash_data[len(self.prefix):]))[self.hash_size:]
        new_password_hash_data = self.get_password_hash(password, salt=salt)
        return new_password_hash_data == password_hash_data

class SMd5PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "md5"
    prefix = "{SMD5}"
    hash_size = 16

class SShaPasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha1"
    prefix = "{SSHA}"
    hash_size = 20

class SSha1PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha1"
    prefix = "{SSHA1}"
    hash_size = 20

class SSha224PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha224"
    prefix = "{SSHA224}"
    hash_size = 28

class SSha256PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha256"
    prefix = "{SSHA256}"
    hash_size = 32

class SSha384PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha384"
    prefix = "{SSHA384}"
    hash_size = 48

class SSha512PasswordHashMethod(SimpleSaltPasswordHashMethod):
    method = "sha512"
    prefix = "{SSHA512}"
    hash_size = 64

class HexlifyPasswordHashMethod(PasswordHashMethodBase):

    length = 40
    method = "sha1"

    def get_password_hash(self, password):
        return get_hash_hexdigest(password, method=self.method)
    
    def validate_password_hash(self, password_hash_data, password):
        from zenutils import strutils
        if not strutils.is_unhexlifiable(password_hash_data):
            return None
        if len(password_hash_data) != self.length:
            return None
        new_password_hash_data = self.get_password_hash(password)
        return new_password_hash_data == password_hash_data

class Md5HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 32
    method = "md5"

class ShaHexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 40
    method = "sha1"

class Sha1HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 40
    method = "sha1"

class Sha224HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 56
    method = "sha224"

class Sha256HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 64
    method = "sha256"

class Sha384HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 96
    method = "sha384"

class Sha512HexlifyPasswordHashMethod(HexlifyPasswordHashMethod):
    length = 128
    method = "sha512"

register_password_hash_method("MD5", Md5PasswordHashMethod())
register_password_hash_method("SHA", ShaPasswordHashMethod())
register_password_hash_method("SHA1", Sha1PasswordHashMethod())
register_password_hash_method("SHA224", Sha224PasswordHashMethod())
register_password_hash_method("SHA256", Sha256PasswordHashMethod())
register_password_hash_method("SHA384", Sha384PasswordHashMethod())
register_password_hash_method("SHA512", Sha512PasswordHashMethod())

register_password_hash_method("SMD5", SMd5PasswordHashMethod())
register_password_hash_method("SSHA", SShaPasswordHashMethod())
register_password_hash_method("SSHA1", SSha1PasswordHashMethod())
register_password_hash_method("SSHA224", SSha224PasswordHashMethod())
register_password_hash_method("SSHA256", SSha256PasswordHashMethod())
register_password_hash_method("SSHA384", SSha384PasswordHashMethod())
register_password_hash_method("SSHA512", SSha512PasswordHashMethod())

register_password_hash_method("PBKDFS2_MD5", Pbkdfs2Md5PasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA", Pbkdfs2ShaPasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA1", Pbkdfs2Sha1PasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA224", Pbkdfs2Sha224PasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA256", Pbkdfs2Sha256PasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA384", Pbkdfs2Sha384PasswordHashMethod())
register_password_hash_method("PBKDFS2_SHA512", Pbkdfs2Sha512PasswordHashMethod())

register_password_hash_method("PBKDFS2:MD5", Pbkdfs2Md5PasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA", Pbkdfs2ShaPasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA1", Pbkdfs2Sha1PasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA224", Pbkdfs2Sha224PasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA256", Pbkdfs2Sha256PasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA384", Pbkdfs2Sha384PasswordHashMethodColon())
register_password_hash_method("PBKDFS2:SHA512", Pbkdfs2Sha512PasswordHashMethodColon())

register_password_hash_method("MD5HEX", Md5HexlifyPasswordHashMethod())
register_password_hash_method("SHAHEX", ShaHexlifyPasswordHashMethod())
register_password_hash_method("SHA1HEX", Sha1HexlifyPasswordHashMethod())
register_password_hash_method("SHA224HEX", Sha224HexlifyPasswordHashMethod())
register_password_hash_method("SHA256HEX", Sha256HexlifyPasswordHashMethod())
register_password_hash_method("SHA384HEX", Sha384HexlifyPasswordHashMethod())
register_password_hash_method("SHA512HEX", Sha512HexlifyPasswordHashMethod())
