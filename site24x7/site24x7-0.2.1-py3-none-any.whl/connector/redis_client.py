import redis
from .models.model import ClientModel

class RedisClient(ClientModel):
    def __init__(self, host, port, db, *args, charset="utf-8", decode_responses=True, **kwargs):
        self.host=host
        self.port=port
        self.db=db
        self.charset=charset
        self.decode_responses=decode_responses
        self.redis=redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            charset=self.charset,
            decode_responses=self.decode_responses
        )
        super().__init__(*args, **kwargs)

    def hset(
        self,
        array_name:str,
        key:str,
        value:str
    ):
        self.redis.hset(array_name, key, value)

    def hgetall(self, array_name:str) -> list:
        return self.redis.hgetall(array_name)

    def get_redis(self) -> redis.Redis:
        return self.redis

    def get_host(self) -> str:
        return self.host

    def get_port(self) -> str:
        return self.port

    def get_db(self) -> str:
        return self.db

    def set_dict_using_global_selector(self, global_selector:str, array_name:str, set_item_key:str):
        array = self.hgetall(array_name)
        for key in array:
            if key.startswith(global_selector):
                self.__setitem__(set_item_key, array[key])
                return
        raise KeyError("Key not found")
