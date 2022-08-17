import redis

from .exceptions import ValueNotOfSupportedType
from .parsing import RedisParsing
from .validations import RedisValidations as Validate

Decode = RedisParsing()


class RedisHashmaps:
    def __init__(self, connection, tenant, key):
        self.__connection = connection
        self.__tenant = tenant
        self.__key = self.__tenant + str(key)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __repr__(self):
        return str(self.getall())

    def __str__(self):
        return str(self.getall())

    # Set a hashmap at a particular key
    def set(self, hash_key, hash_value):
        if Validate.key_validation(hash_key) and Validate.value_validation(hash_value):
            return self.__connection.hset(self.__key, hash_key, hash_value)

    # Get a value from a given key in the hashmap
    def get(self, hash_key):
        if Validate.key_validation(hash_key):
            return Decode.parse(self.__connection.hget(self.__key, hash_key))

    # Set multiple values in the hashmap like hash_map_key {key_1: value_1, key_2: value_2}
    def mset(self, mapping):
        if isinstance(mapping, dict):
            if (all(list(map(Validate.key_validation, mapping.keys())))
               and all(list(map(Validate.value_validation, mapping.values())))):
                return self.__connection.hmset(self.__key, mapping)
        else:
            raise ValueNotOfSupportedType("Mapping not of the supported format")

    # Set multiple values in the hashmap like hash_map_key key_1 key_2
    def mget(self, *key_values):
        if all(list(map(Validate.key_validation, key_values))):
            return Decode.parse(self.__connection.hmget(self.__key, key_values))

    # Get all keys and values
    def getall(self):
        return Decode.parse(self.__connection.hgetall(self.__key))

    # Check if a key exists in a hashmap
    def exists(self, hash_key):
        if Validate.key_validation(hash_key):
            return self.__connection.hexists(self.__key, hash_key)

    # Increment or Decrement a value by a certain amount in the hashmap
    def incrby(self, hash_key, amount=1):
        if Validate.key_validation(hash_key):
            if self.__isint(amount):
                try:
                    return self.__connection.hincrby(self.__key, hash_key, amount)
                except redis.exceptions.ResponseError:
                    raise ValueNotOfSupportedType("The value is not an integer or out of range")
            else:
                raise ValueNotOfSupportedType("The increment amount should be an integer")

    # Get all keys in the hashmap
    def keys(self):
        return Decode.parse(self.__connection.hkeys(self.__key))

    # Get all values in the hashmap
    def vals(self):
        return Decode.parse(self.__connection.hvals(self.__key))
