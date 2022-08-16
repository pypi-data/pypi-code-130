from abc import ABC, abstractmethod
from requests import Session, Response


class APIEndpoint(ABC):
    def __init__(self, session: Session):
        self.client = session

    @abstractmethod
    def get_by_id(self, id):
        raise NotImplementedError


class FormattedObject(ABC):
    @abstractmethod
    def formatted(self):
        raise NotImplementedError


class UserGroup(FormattedObject):
    name = "user_group_name"
    meta = {
        "foo": "bar"
    }

    def formatted(self):
        return f"{self.name} | {self.meta.get('foo')}"


class UserGroups(APIEndpoint):
    def get_by_id(self, id) -> UserGroup:
        response = self.client.get(f"https://api.logichub.com/usergroups/{id}")
        return response


class Alerts(APIEndpoint):
    def get_by_id(self, id) -> Response:
        response = self.client.get(f"https://api.logichub.com/alerts/{id}")
        return response


class LogicHubClient:
    def __init__(self, hostname, api_key):
        session = Session()
        session.headers.update(
            {"Authorization": f"Bearer {api_key}"}
        )

        self.client = session
        self.user_groups = UserGroups(session=session)
        self.alerts = Alerts(session=session)


lh_client = LogicHubClient("somehostname", "myapikey1234")
usergroup = lh_client.user_groups.get_by_id(1234)

print(usergroup.formatted())