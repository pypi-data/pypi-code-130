from datetime import datetime
import time
import random
DEFALT_LENGTH = 8


class ShortId:
    def __init__(self, shard: int = 60, start_date: datetime = datetime(2010, 1, 1)) -> None:
        self.start_timestamp_block = round(start_date.timestamp() * 10)
        self.shard = shard
        self.alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.alpha_len = len(self.alpha)
        pass

    def string_to_int(self, string: str) -> int:
        number = 0
        for char in string:
            number = number * self.alpha_len + self.alpha.index(char)
        return number

    def int_to_string(self, number: int):
        output = ""
        while number:
            number, digit = divmod(number, self.alpha_len)
            output += self.alpha[digit]
        return output[::-1]

    def string_from_timestamp(self):
        number = round(time.time() * 10) - \
            self.start_timestamp_block
        return self.int_to_string(number=number)

    def get_shard_seq(self, rand_id):
        return self.string_to_int(rand_id) % self.shard

    def rand_string(self, l):
        return "".join(random.choices(self.alpha, k=l))

    def id(self, l: int = DEFALT_LENGTH):
        _id, _ = self.id_with_shard(l=l)
        return _id

    def id_with_shard(self, l: int = DEFALT_LENGTH):
        time_id = self.string_from_timestamp()
        if(l < 7):
            rand_id_l = 2
        else:
            rand_id_l = l - len(time_id)

        rand_id = self.rand_string(l=rand_id_l)
        shard_seq = self.string_to_int(rand_id) % self.shard

        return "{}{}".format(time_id, rand_id)[-l:], shard_seq

    def decode(self, id: str):
        time_id = None
        timestamp = None
        dt = None
        if len(id) >= 7:
            time_id = id[0:6]
            timestamp = (self.string_to_int(time_id) +
                         self.start_timestamp_block) / 10
            dt = datetime.fromtimestamp(timestamp)
            random_string = id[len(time_id):]
        else:
            random_string = id[-2:]

        random_seq = self.string_to_int(random_string)
        shard_seq = random_seq % self.shard

        return {"shard_seq": shard_seq,
                "dt": dt,
                "random_string": random_string,
                "random_seq": random_seq}
