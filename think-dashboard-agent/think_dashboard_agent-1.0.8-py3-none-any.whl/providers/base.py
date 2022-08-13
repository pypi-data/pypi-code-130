from think_dashboard_agent import types


class BaseProvider:

    @classmethod
    def init(cls, instance: types.BaseInstance) -> "BaseProvider":
        raise NotImplementedError()

    def connect(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def exc(self, connection):
        raise NotImplementedError()

    def check(self, auto_close: bool = True) -> types.InstanceCheckResult:
        raise NotImplementedError()
