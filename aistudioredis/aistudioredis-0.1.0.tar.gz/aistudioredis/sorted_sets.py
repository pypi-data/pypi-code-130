from .exceptions import ValueNotOfSupportedType
from .parsing import RedisParsing
from .validations import RedisValidations as Validate

Decode = RedisParsing()


class RedisSortedSets:
    def __init__(self, connection, tenant, key):
        self.__connection = connection
        self.__tenant = tenant
        self.__org_key = key
        self.__key = self.__tenant + str(key)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.range(index, index, withscores=True)
        elif isinstance(index, slice):
            return self.range(index.start, index.stop, withscores=True)

    def __or__(self, other_set):
        return self.unionstore(self.__org_key, [self.__org_key, other_set.key()])

    def __and__(self, other_set):
        return self.interstore(self.__org_key, [self.__org_key, other_set.key()])

    def __repr__(self):
        return str(self.range(withscores=True))

    def __str__(self):
        return str(self.range(withscores=True))

    def key(self):
        return self.__org_key

    # Add multiple elements to a sorted set, Mappings are of form {value_1: score_1, value_2: score_2}
    def add(self, mapping):
        if isinstance(mapping, dict):
            if (all(list(map(Validate.key_validation, mapping.keys())))
               and all(list(map(Validate.value_validation, mapping.values())))):
                return self.__connection.zadd(self.__key, mapping)
        else:
            raise ValueNotOfSupportedType("Mapping should be a dictionary")

    # Get multiple elements from the sorted set
    def range(self, start=0, end=-1, desc=False, withscores=False):
        if Validate.isint(start):
            if Validate.isint(end):
                if isinstance(desc, bool):
                    if isinstance(withscores, bool):
                        return Decode.parse(
                            self.__connection.zrange(
                                self.__key, start, end, desc=desc, withscores=withscores
                            )
                        )
                    else:
                        raise ValueNotOfSupportedType("Withscores should have a boolean value")
                else:
                    raise ValueNotOfSupportedType("Desc should have a boolean value")
            else:
                raise ValueNotOfSupportedType("End should be an integer")
        else:
            raise ValueNotOfSupportedType("Start should be an integer")

    # Remove multiple values from the sorted set
    def rem(self, *values):
        if all(list(map(Validate.value_validation, values))):
            return self.__connection.zrem(self.__key, *values)

    # Union of multiple sorted sets and store to database
    def unionstore(self, dest_key, keys):
        all_keys = [dest_key, *keys]
        if all(list(map(Validate.key_validation, all_keys))):
            dest_key = self.__tenant+str(dest_key)
            keys = list(map(lambda x: self.__tenant+str(x), keys))
            print(dest_key, keys)
            return self.__connection.zunionstore(dest_key, keys)

    # Intersection of multiple sorted sets and store to database
    def interstore(self, dest_key, keys):
        all_keys = [dest_key, *keys]
        if all(list(map(Validate.key_validation, all_keys))):
            dest_key = self.__tenant+str(dest_key)
            keys = list(map(lambda x: self.__tenant+str(x), keys))
            print(dest_key, keys)
            return self.__connection.zinterstore(dest_key, keys)

    # Cardinality of the sorted set
    def card(self):
        return self.__connection.zcard(self.__key)

    # Score of a particular value of the sorted set
    def score(self, value):
        if Validate.value_validation(value):
            return self.__connection.zscore(self.__key, value)

    # Rank(Position) of a particular element in the sorted set
    def rank(self, value):
        if Validate.value_validation(value):
            return self.__connection.zrank(self.__key, value)
