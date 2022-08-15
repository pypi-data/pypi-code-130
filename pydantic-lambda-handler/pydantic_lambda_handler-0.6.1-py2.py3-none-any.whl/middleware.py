from typing import Any


class BaseHook:
    def method_init(self, **kwargs) -> None:
        return

    def pre_path(self, **kwargs) -> None:
        return

    def pre_func(self, event, context) -> tuple[dict, Any]:
        return event, context

    def post_func(self, body) -> Any:
        return body
