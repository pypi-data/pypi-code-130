from .exceptions import ValueNotOfSupportedType
from .parsing import RedisParsing
from .validations import RedisValidations as Validate

Decode = RedisParsing()


class RedisLists:
    def __init__(self, connection, tenant, key):
        self.__connection = connection
        self.__tenant = tenant
        self.__key = self.__tenant + str(key)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.index(index)
        elif isinstance(index, slice):
            return self.range(index.start, index.stop)

    def __setitem__(self, index, value):
        return self.set(index, value)

    def __repr__(self):
        return str(self.range())

    def __str__(self):
        return str(self.range())

    # Push an element at the beginning of a list
    def push(self, value):
        if Validate.value_validation(value):
            return self.__connection.lpush(self.__key, value)

    # Pop an element from the beginning of a list
    def pop(self):
        return Decode.parse(self.__connection.lpop(self.__key))

    # Get the number of elements in the list
    def len(self):
        return self.__connection.llen(self.__key)

    # Get an element at a particular index in the list
    def index(self, index):
        if Validate.isint(index):
            return Decode.parse(self.__connection.lindex(self.__key, index))
        else:
            raise ValueNotOfSupportedType("Index should be of type int")

    # Insert a element before or after a particular element in the list
    def insert(self, index, element_value, value):
        if isinstance(index, str):
            index = index.lower()
            if index in ['before', 'after']:
                if isinstance(element_value, (int, float, str, bytes)):
                    if Validate.value_validation(value):
                        return self.__connection.linsert(self.__key, index, element_value, value)
                else:
                    raise ValueNotOfSupportedType("Inserted value should be of type int, float, str or bytes")
            else:
                raise ValueNotOfSupportedType(
                    "Index should be a string 'before' or 'after'")
        else:
            raise ValueNotOfSupportedType(
                "Index should be a string 'before' or 'after'")

    # Push an element from the right of the list
    def rpush(self, value):
        if Validate.value_validation(value):
            return self.__connection.rpush(self.__key, value)

    # Pop an element from the right of the list
    def rpop(self):
        return Decode.parse(self.__connection.rpop(self.__key))

    # Trim the list from a start index to an end index
    def trim(self, start=0, end=-1):
        if Validate.isint(start):
            if Validate.isint(end):
                return self.__connection.ltrim(self.__key, start, end)
            else:
                raise ValueNotOfSupportedType("End should be an integer")
        else:
            raise ValueNotOfSupportedType("Start should be an integer")

    # Get the elements of the list from the start position to the end position
    def range(self, start=0, end=-1):
        if Validate.isint(start):
            if Validate.isint(end):
                return Decode.parse(self.__connection.lrange(self.__key, start, end))
            else:
                raise ValueNotOfSupportedType("End should be an integer")
        else:
            raise ValueNotOfSupportedType("Start should be an integer")

    # Set the element at a particular index
    def set(self, index, value):
        if Validate.isint(index) and Validate.value_validation(value):
            return self.__connection.lset(self.__key, index, value)

    # Remove elements corresponding to a value given. Give count = 0 to remove
    # all values. +ve to remove from head to tail and -ve to remove from tail to head
    def rem(self, count, value):
        if Validate.isint(count) and Validate.value_validation(value):
            return self.__connection.lrem(self.__key, count, value)
