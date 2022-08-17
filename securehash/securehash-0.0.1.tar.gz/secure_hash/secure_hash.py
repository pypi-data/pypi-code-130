import bcrypt ## Bcrypt for anti-bruteforce hashing
import hashlib ## Hashlib for sha256 hashing
import base64
import hmac ## Hmac for comparing hashes


def get_salt(hash0):
    return hash0[:29] ## First 29 characters are the salt
    

def hash_low(password, salt, pepper=""):
    return bcrypt.hashpw(base64.b64encode(hashlib.sha256((password+pepper).encode("utf-8")).digest()), salt) ## sha256 so we don't go over char limit


def verify_low(password, hash0, salt, pepper=""):
    return hmac.compare_digest(hash0, hash_low(password, salt, pepper)) ## hmac.compare_digest to avoid timing attacks (or atleast make them less effective)


def hash_high(password, pepper="", rounds=None):
    if rounds == None:
        return hash_low(password, bcrypt.gensalt(), pepper)
    else:
        return hash_low(password, bcrypt.gensalt(rounds), pepper) ## Custom number of rounds for salt generation


def verify_high(password, hash0, pepper=""):
    return verify_low(password, hash0, get_salt(hash0), pepper)




### Test zone, you probably don't need it

def test(): ## Test function to test all other functions
    salt = bcrypt.gensalt()
    print(salt)
    hash0 = hash_low("mypass", salt, "mypepper")
    print(hash0)
    hash1 = hash_high("mypass", "mypepper")
    print(hash1)
    hash0v = verify_low("mypass", hash0, salt, "mypepper")
    print(hash0v)
    hash1v = verify_high("mypass", hash1, "mypepper")
    print(hash1v)
    hash2 = hash_high("mypass", "mypepper", 4) # Test rounds parameter working
    print(hash2)
    hash2v = verify_high("mypass", hash2, "mywrongpepper") # Test for wrong pepper detection
    print(hash2v)
    hash3 = hash_high("mypass", "mypepper")
    print(hash3)
    hash3v = verify_high("mywrongpass", hash3, "mypepper") # Test for wrong password detection
    print(hash3v)

def hash_low_verbose(password, salt, pepper=""):
    x = (password+pepper).encode("utf-8")
    print(x)
    y = hashlib.sha256(x).digest()
    print(y)
    yy= base64.b64encode(y)
    z = bcrypt.hashpw(yy, salt)
    print(z)
    return z

def hash_high_verbose(password, pepper="", rounds=None):
    if rounds == None:
        return hash_low_verbose(password, bcrypt.gensalt(), pepper)
    else:
        return hash_low_verbose(password, bcrypt.gensalt(rounds), pepper)

def verify_high_verbose(password, hash0, pepper=""):
    return verify_low_verbose(password, hash0, get_salt(hash0), pepper)

def verify_low_verbose(password, hash0, salt, pepper=""):
    return hmac.compare_digest(hash0, hash_low_verbose(password, salt, pepper))
