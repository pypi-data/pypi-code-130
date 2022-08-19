from cryptography.fernet import Fernet
from codex_taps.__init__ import *

def decrypt(ciphertext):
    cipher = Fernet(key)
    
    return cipher.decrypt(ciphertext.encode()).decode()