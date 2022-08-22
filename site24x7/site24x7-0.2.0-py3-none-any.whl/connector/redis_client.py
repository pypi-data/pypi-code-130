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

    def set(
        self,
        arrayName:str,
        key:str,
        value:str
    ):
        self.redis.hset(arrayName, key, value)

    def get(self, arrayName:str) -> list:
        return self.redis.hgetall(arrayName)

    def _getRedisClient(self) -> redis.Redis:
        return self.redis

    def getHost(self) -> str:
        return self.host
