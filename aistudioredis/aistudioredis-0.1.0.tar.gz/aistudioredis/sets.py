from .exceptions import ValueNotOfSupportedType
from .parsing import RedisParsing
from .validations import RedisValidations as Validate

Decode = RedisParsing()


class RedisSets:
    def __init__(self, connection, tenant, key):
        self.__connection = connection
        self.__tenant = tenant
        self.__org_key = key
        self.__key = self.__tenant + str(key)

    def __sub__(self, other_set):
        return self.diffstore(self.__org_key, other_set.key())

    def __or__(self, other_set):
        return self.unionstore(self.__org_key, other_set.key())

    def __and__(self, other_set):
        return self.interstore(self.__org_key, other_set.key())

    def __repr__(self):
        return str(self.members())

    def __str__(self):
        return str(self.members())

    def key(self):
        return self.__org_key

    # Add one or more elements to the set
    def add(self, *values):
        if all(list(map(Validate.value_validation, values))):
            return self.__connection.sadd(self.__key, *values)

    # Remove one or more elements from the set
    def rem(self, *values):
        if all(list(map(Validate.value_validation, values))):
            return self.__connection.srem(self.__key, *values)

    # Move the value from current set to another set
    def move(self, set_key, value):
        if Validate.key_validation(set_key) and Validate.value_validation(value):
            return self.__connection.smove(self.__key, self.__tenant+str(set_key), value)

    # Get the number of elements in the set
    def card(self):
        return self.__connection.scard(self.__key)

    # Get all the elements in the set
    def members(self):
        return Decode.parse(self.__connection.smembers(self.__key))

    # Check if an element is present in the set
    def ismember(self, value):
        if Validate.value_validation(value):
            return self.__connection.sismember(self.__key, value)

    # Pop one or more elements from the set
    def pop(self, count=1):
        if Validate.isint(count):
            return Decode.parse(self.__connection.spop(self.__key, count))
        else:
            raise ValueNotOfSupportedType("Count should be an integer")

    # Difference between two or more sets and return to client
    def diff(self, *all_keys):
        if all(list(map(Validate.key_validation, all_keys))):
            all_keys = list(map(lambda x: self.__tenant+str(x), all_keys))
            return Decode.parse(self.__connection.sdiff(self.__key, *all_keys))

    # Difference between two or more sets and store to dest variable provided
    def diffstore(self, dest, *keys):
        if Validate.key_validation(dest):
            dest = self.__tenant+str(dest)
            if all(list(map(Validate.key_validation, keys))):
                keys = list(map(lambda x: self.__tenant+str(x), keys))
                return self.__connection.sdiffstore(dest, self.__key, *keys)

    # Union of two or more sets and return to client
    def union(self, *all_keys):
        if all(list(map(Validate.key_validation, all_keys))):
            all_keys = list(map(lambda x: self.__tenant+str(x), all_keys))
            return Decode.parse(self.__connection.sunion(self.__key, *all_keys))

    # Union of two or more sets and store to dest variable provided
    def unionstore(self, dest, *keys):
        if Validate.key_validation(dest):
            dest = self.__tenant+str(dest)
            if all(list(map(Validate.key_validation, keys))):
                keys = list(map(lambda x: self.__tenant+str(x), keys))
                return self.__connection.sunionstore(dest, self.__key, *keys)

    # Intersection of two or more sets and return to client
    def inter(self, *all_keys):
        if all(list(map(Validate.key_validation, all_keys))):
            all_keys = list(map(lambda x: self.__tenant+str(x), all_keys))
            return Decode.parse(self.__connection.sinter(self.__key, *all_keys))

    # Intersection of two or more sets and store to dest provided
    def interstore(self, dest, *keys):
        if Validate.key_validation(dest):
            dest = self.__tenant+str(dest)
            if all(list(map(Validate.key_validation, keys))):
                keys = list(map(lambda x: self.__tenant+str(x), keys))
                return self.__connection.sinterstore(dest, self.__key, *keys)
