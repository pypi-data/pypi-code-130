import socket
import ssl
from datetime import datetime

from think_dashboard_agent.providers.base import BaseProvider
from think_dashboard_agent.types import SSLInstance, InstanceCheckResult


class SSLProvider(BaseProvider):
    def __init__(self, instance: SSLInstance):
        self.instance = instance
        self.__connection = None

    @classmethod
    def init(cls, instance: SSLInstance) -> "SSLProvider":
        return cls(instance)

    def connect(self):
        if self.__connection is None:
            context = ssl.create_default_context()
            self.__connection = context.wrap_socket(
                socket.socket(socket.AF_INET),
                server_hostname=self.instance.host,
            )
            self.__connection.settimeout(3.0)
            self.__connection.connect((self.instance.host, self.instance.port))
        return self.__connection

    def close(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    def exc(self, connection):
        ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
        ssl_info = connection.getpeercert()
        expires = datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        return expires.strftime('%Y-%m-%d %H:%M:%S')

    def check(self, auto_close: bool = True) -> InstanceCheckResult:

        try:
            connection = self.connect()
            r = self.exc(connection)
            return InstanceCheckResult(status=200, data=r)
        except Exception as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            if auto_close:
                self.close()
