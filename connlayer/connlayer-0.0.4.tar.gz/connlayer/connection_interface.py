import constants


class ConnectionInterface(object):

    def __init__(self, name: str, config: str):
        self.name = name
        self.config = config
        if name == constants.redis_name:
            self.client = self.get_redis_client(config)
        elif name == constants.cosmos_name:
            self.client = self.get_cosmos_client(config)
        elif name == constants.mysql_name:
            self.client = self.get_mysql_client(config)
        elif name == constants.postgres_name:
            self.client = self.get_mysql_client(config)

    @staticmethod
    def get_redis_client(config: dict):
        return config

    @staticmethod
    def get_cosmos_client(config: dict):
        return config

    @staticmethod
    def get_mysql_client(config: dict):
        return config

    @staticmethod
    def get_postgres_client(config: dict):
        return config
