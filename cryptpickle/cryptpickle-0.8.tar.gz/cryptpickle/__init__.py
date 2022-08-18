"""
Library for encrypted python object serialization.

CryptPickle allows you to easily encrypt python objects into a file and decrypt,
regardless of their content.
It may be any python object, including for example a Pandas DataFrame.
"""


__version__ = "0.8"


import pickle
import string
import pyzipper

DATA_PATH = "./data.crypt"
NO_PASSWD = None


def obj_to_encrypted(obj, password=NO_PASSWD, path=DATA_PATH):
    """Encrypt object data to file"""
    buf = pickle.dumps(obj)
    pwd = password
    with pyzipper.AESZipFile(path,
                         'w',
                         compression=pyzipper.ZIP_DEFLATED,
                         encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(pwd.encode('utf-8'))
        zf.writestr('data', buf)


def obj_from_encrypted(password=NO_PASSWD, path=DATA_PATH):
    """Decrypt object data to file"""
    pwd = password
    with pyzipper.AESZipFile(path) as zf:
        zf.setpassword(pwd.encode('utf-8'))
        buf = zf.read('data')
    return pickle.loads(buf)
