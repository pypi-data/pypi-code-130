from edwardsserial.serial_protocol import SerialProtocol


class SerialQuery:
    """
    Desciptor protocol for a query command that returns a single value or a list of values of the same data_type.
    """

    def __init__(self, operation, object_id, data_type):
        self.operation = operation
        self.object_id = object_id
        self.data_type = data_type

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance: SerialProtocol, owner: SerialProtocol):
        if instance is None:
            return self
        else:
            ret_val = list(
                map(
                    self.data_type,
                    instance.send_message("?" + self.operation, self.object_id),
                )
            )
            if len(ret_val) == 1:
                return ret_val[0]
            return ret_val


class ValueRange(SerialQuery):
    """
    Inherits from SerialQuery, can be used to set values.
    Checks if assigned value is in a certain range and raises ValueError if not.
    """

    def __init__(self, start, end, **kwargs):
        super().__init__(data_type=int, **kwargs)
        self.start = start
        self.end = end
        self.__doc__ = f"Value in {range(self.start, self.end + 1)}]"

    def __set__(self, instance, value):
        if value not in range(self.start, self.end + 1):
            raise ValueError(
                f"Value for '{self.name}' must be in {range(self.start, self.end + 1)}"
            )
        instance.send_message("!" + self.operation, self.object_id, data=value)
