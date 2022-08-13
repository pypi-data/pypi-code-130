import redis

from think_dashboard_agent.types import RedisInstance, InstanceCheckResult
from .base import BaseProvider


class RedisProvider(BaseProvider):
    def __init__(self, instance: RedisInstance):
        self.instance = instance
        self.__connection = None

    @classmethod
    def init(cls, instance: RedisInstance) -> "RedisProvider":
        return cls(instance)

    def connect(self):
        if self.__connection is not None:
            try:
                self.__connection.ping()
            except redis.exceptions.ConnectionError:
                self.__connection = None
        if self.__connection is None:
            self.__connection = redis.Redis(
                host=self.instance.host,
                port=self.instance.port,
                password=self.instance.password,
                db=self.instance.db
            )
        return self.__connection

    def exc(self, connection: redis.Redis) -> dict:
        return connection.execute_command('PING')

    def check(self, auto_close: bool = True) -> InstanceCheckResult:
        try:
            connection = self.connect()
            r = self.exc(connection)
            return InstanceCheckResult(data=r)
        except redis.RedisError as e:
            return InstanceCheckResult(status=500, data={'error': str(e)})
        finally:
            if auto_close:
                self.close()

    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
