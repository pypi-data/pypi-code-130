from enum import Enum

class TokenType(Enum):
    COMMAND = 0
    COMPONENT_TYPE = 1
    ARGUMENT = 2
    TAG = 3
    VALUE = 4
    NAMED_ARGUMENT = 5
    UNKNOWN = 6
    ERROR = 7

class Token():

    def __init__(self, token_type, token_value):
        self.token_type = token_type
        self.token_value = token_value

    def __str__(self):
        if isinstance(self.token_value, str):
            return self.token_value
        elif isinstance(self.token_value, tuple):
            return str(self.token_value)
        else:
            return str(self.token_value)

    def is_valid(self):
        return self.token_type == TokenType.ERROR

    def clean_token(self):
        if self.token_type == TokenType.NAMED_ARGUMENT:
            self.token_value = (self.token_value[0], self.token_value[1].replace('"','').strip())