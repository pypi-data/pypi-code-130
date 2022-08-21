import datetime
import string
import random

DEFALT_LENGTH = 8
BASE_LEN = 6
AZ09 = string.ascii_letters + string.digits
LEN_AZ09 = 62


class ShortId:
    def __init__(self) -> None:
        pass

    def convert_index_to_id(self, index):
        result = ""
        step = 2
        for i in range(0, len(index), step):
            c_index = int(index[i:i+step])
            result += AZ09[c_index]
        return result

    def random_n_index(self, n):
        result = ""
        while(n > 0):
            result += str(random.randint(0, LEN_AZ09 - 1)).zfill(2)
            n -= 1
        return result

    def id(self, l=8):
        if l == None:
            l = DEFALT_LENGTH

        date_now = datetime.datetime.now()
        base_index = date_now.strftime("%d%m%y%H%M%S")
        random_index = self.random_n_index(n=(l - BASE_LEN))
        index = base_index + random_index
        return self.convert_index_to_id(index=index)
