class HttpError(Exception):
    pass


class SSLError(HttpError):
    pass


class ProtocolError(HttpError):
    pass


class RemoteDisconnected(ProtocolError):
    pass


class TimeoutError(HttpError):
    # pylint: disable=redefined-builtin
    pass


class ConnectTimeoutError(TimeoutError):
    pass


class ReadTimeoutError(TimeoutError):
    pass


class NewConnectionError(ConnectTimeoutError):
    pass


class LocationValueError(HttpError, ValueError):
    pass


class PoolError(HttpError):
    pass


class EmptyPoolError(PoolError):
    pass


class ClosedPoolError(PoolError):
    pass


class HostChangedError(PoolError):
    pass
