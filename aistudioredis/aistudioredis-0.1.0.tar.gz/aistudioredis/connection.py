import redis

from .exceptions import ConflictingDataDetected, ValueNotOfSupportedType
from .hashmaps import RedisHashmaps
from .lists import RedisLists
from .parsing import RedisParsing
from .sets import RedisSets
from .sorted_sets import RedisSortedSets
from .validations import RedisValidations as Validate

Decode = RedisParsing()


class RedisConnection:
    # Setting up the connection, pubsub configuration and tenant prefix
    def __init__(self, host="localhost", port=6379, db=0, pool=True, tenant=""):
        if pool is True:
            connection_pool = redis.ConnectionPool(host=host, port=port, db=db)
            self.__connection = redis.Redis(connection_pool=connection_pool)
        else:
            self.__connection = redis.Redis(host=host, port=port, db=db)
        self.__pubsub = self.__connection.pubsub()
        if len(tenant) != 0:
            self.__tenant = tenant + ":"
        else:
            self.__tenant = tenant

    # Verify if a key exists
    def exists(self, key):
        if Validate.key_validation(key):
            return self.__connection.exists(self.__tenant+str(key))

    # Set a value to a key
    def set(self, key, value):
        if Validate.key_validation(key) and Validate.value_validation(value):
            return self.__connection.set(self.__tenant+str(key), value)
        else:
            raise ValueNotOfSupportedType(
                "Timeout should be of type int or float")

    # Append a value to an already stored value (concats strings)
    def append(self, key, value):
        if Validate.key_validation(key) and Validate.value_validation(value):
            return self.__connection.append(self.__tenant+str(key), value)

    # Get a value by key
    def get(self, key):
        if Validate.key_validation(key):
            value = self.__connection.get(self.__tenant+str(key))
            return Decode.parse(value)

    # Decrement a value if it is an integer
    def decr(self, key, amount=1):
        if Validate.key_validation(key):
            if Validate.isint(amount):
                try:
                    return self.__connection.decr(self.__tenant+str(key), amount)
                except redis.exceptions.ResponseError:
                    raise ValueNotOfSupportedType("The value is not an integer or out of range")
            else:
                raise ValueNotOfSupportedType("The decrement amount should be an integer")

    # Increment a value by an amount if it is an integer
    def incr(self, key, amount=1):
        if Validate.key_validation(key):
            if Validate.isint(amount):
                try:
                    return self.__connection.incr(self.__tenant+str(key), amount)
                except redis.exceptions.ResponseError:
                    raise ValueNotOfSupportedType("The value is not an integer or out of range")
            else:
                raise ValueNotOfSupportedType("The increment amount should be an integer")

    # Retrieve all keys
    def keys(self, regex="*"):
        prefix_length = len(self.__tenant)
        return list(map(lambda x: Decode.parse(x[prefix_length:]), self.__connection.keys(self.__tenant+regex)))

    # Get the length of the value of the string
    def strlen(self, key):
        if Validate.key_validation(key):
            return self.__connection.strlen(self.__tenant+str(key))

    # Get the type of the data stored
    def type(self, key):
        if Validate.key_validation(key):
            return Decode.parse(self.__connection.type(self.__tenant+str(key)))

    # Delete a key
    def delete(self, key):
        if Validate.key_validation(key):
            return self.__connection.delete(self.__tenant+str(key))

    # Delete all keys of a tenant
    def delete_all(self, regex="*"):
        keys = self.__connection.keys(self.__tenant+regex)
        return self.__connection.delete(*keys)

    # Flush the entire database
    def flushdb(self):
        return self.__connection.flushdb()

    def RedisList(self, key, force=False):
        if Validate.key_validation(key):
            if self.exists(key) and self.type(key) != "list":
                if force is True:
                    self.delete(key)
                else:
                    raise ConflictingDataDetected(
                        "Setting data of type 'list' failed because data of type '"
                        + str(self.type(key)) + "' detected at key '" + str(key) + "'"
                    )
            return RedisLists(self.__connection, self.__tenant, key)

    def RedisSet(self, key, force=False):
        if Validate.key_validation(key):
            if self.exists(key) and self.type(key) != "set":
                if force is True:
                    self.delete(key)
                else:
                    raise ConflictingDataDetected(
                        "Setting data of type 'set' failed because data of type '"
                        + str(self.type(key)) + "' detected at key '" + str(key) + "'"
                    )
            return RedisSets(self.__connection, self.__tenant, key)

    def RedisHashmap(self, key, force=False):
        if Validate.key_validation(key):
            if self.exists(key) and self.type(key) != "hash":
                if force is True:
                    self.delete(key)
                else:
                    raise ConflictingDataDetected(
                        "Setting data of type 'hash' failed because data of type '"
                        + str(self.type(key)) + "' detected at key '" + str(key) + "'"
                    )
            return RedisHashmaps(self.__connection, self.__tenant, key)

    def RedisSortedSet(self, key, force=False):
        if Validate.key_validation(key):
            if self.exists(key) and self.type(key) != "zset":
                if force is True:
                    self.delete(key)
                else:
                    raise ConflictingDataDetected(
                        "Setting data of type 'zset' failed because data of type '"
                        + str(self.type(key)) + "' detected at key '" + str(key) + "'"
                    )
            return RedisSortedSets(self.__connection, self.__tenant, key)

    # Publish a message to a channel
    def publish(self, channel_name, message):
        return self.__connection.publish(channel_name, message)

    # Pattern Subscribe and run in threads
    def run_in_thread(self, channel_name='*', event_handler=lambda msg: print(Decode.parse(msg)), sleep_time=0.01):
        self.__pubsub.psubscribe(**{channel_name: event_handler})
        self.__thread = self.__pubsub.run_in_thread(sleep_time=sleep_time)
        return self.__thread

    # Stop Thread
    def stop_thread(self):
        if self.__thread is not None:
            self.__thread.stop()
            self.__thread = None
