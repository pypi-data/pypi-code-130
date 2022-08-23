import http.client
import socket

from dynatrace.opentelemetry.tracing._transport.connection import (
    BaseSSLError,
    SSLError,
)
from dynatrace.opentelemetry.tracing._transport.exceptions import (
    ProtocolError,
    ReadTimeoutError,
)


class HttpResponse:
    def __init__(self, response: http.client.HTTPResponse):
        self.status = response.status
        self.headers = response.headers
        self.version = response.version
        self.reason = response.reason
        self.data = self._read_response(response)

    @staticmethod
    def _read_response(response: http.client.HTTPResponse):
        clean_exit = False
        try:
            data = response.read()
            clean_exit = True
            return data
        except socket.timeout as ex:
            raise ReadTimeoutError("Read timed out.") from ex
        except BaseSSLError as ex:
            # FIXME: Is there a better way to differentiate between SSLErrors?
            if "read operation timed out" not in str(ex):
                # SSL errors related to framing/MAC get wrapped and reraised here
                raise SSLError(ex)
            raise ReadTimeoutError("Read timed out.") from ex
        except (http.client.HTTPException, socket.error) as ex:
            # This includes IncompleteRead.
            raise ProtocolError(f"Connection broken: {ex!r}", ex)
        finally:
            if not clean_exit:
                response.close()
