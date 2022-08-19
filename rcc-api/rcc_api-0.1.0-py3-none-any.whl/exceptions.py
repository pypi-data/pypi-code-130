class RCCErrors(Exception):
    pass


class RCCStatusError(RCCErrors):
    """Вызывается, когда статус ответа равняется error"""


class PlayerInfoNotFound(RCCStatusError):
    """Вызывается, когда не было найдено информации об игроке"""


class ReasonLenError(RCCErrors):
    """Вызывается, когда длина причины бана превышает 60 символов"""
