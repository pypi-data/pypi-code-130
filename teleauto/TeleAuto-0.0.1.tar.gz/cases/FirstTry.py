import random
import string

def printRandom():
    s="".join(random.sample(string.ascii_letters + string.digits, 8))
    print("随机数："+s)