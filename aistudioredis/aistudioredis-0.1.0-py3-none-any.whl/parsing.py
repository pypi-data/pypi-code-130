from .validations import RedisValidations as Validate


class RedisParsing:
    # Convert the decoded values into their respective types
    def parse(self, data):
        if Validate.isint(data):
            return int(data)
        if Validate.isfloat(data):
            return float(data)
        if isinstance(data, bytes):
            return data.decode('utf-8')
        if isinstance(data, set):
            return set(map(self.parse, data))
        if isinstance(data, dict):
            return dict(map(self.parse, data.items()))
        if isinstance(data, tuple):
            return tuple(map(self.parse, data))
        if isinstance(data, list):
            return list(map(self.parse, data))
        return data
