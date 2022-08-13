import requests

from think_dashboard_agent.types import ElasticSearchInstance, InstanceCheckResult
from .base import BaseProvider


class ElasticSearchProvider(BaseProvider):
    def __init__(self, instance: ElasticSearchInstance):
        self.instance = instance
        self.__connection = None

    @classmethod
    def init(cls, instance: ElasticSearchInstance) -> "ElasticSearchProvider":
        return cls(instance)

    def connect(self):
        if not self.__connection:
            session = requests.Session()
            session.auth = (self.instance.username, self.instance.password)
            session.headers.update({'Content-Type': 'application/json'})
            self.__connection = session
        return self.__connection

    def close(self):
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    def exc(self, session: requests.Session):
        return session.get(f"{self.instance.host}:{self.instance.port}/_cluster/health")

    def check(self, auto_close: bool = True) -> InstanceCheckResult:
        try:
            session = self.connect()
            r = self.exc(session)
            if r.status_code == 200:
                return InstanceCheckResult(status=200, data=r.json())
            else:
                return InstanceCheckResult(status=r.status_code, error=r.text)
        except requests.exceptions.RequestException as e:
            return InstanceCheckResult(status=500, error=str(e))
        finally:
            if auto_close:
                self.close()
