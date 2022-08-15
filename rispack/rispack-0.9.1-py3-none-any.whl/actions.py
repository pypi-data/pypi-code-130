from typing import List, Union

from rispack.events import BaseEvent
from rispack.schemas import BaseSchema
from rispack.stores import scoped_session


class BaseAction:
    def __init__(self):
        self.events: List[BaseEvent] = []

    def publish(self, event: BaseEvent, payload: Union[dict, BaseSchema]):
        event_to_publish = event.load(payload)

        self.events.append(event_to_publish)

    @classmethod
    def run(cls, params):
        action = cls()

        action_runner = action._scoped(params)

        if len(action_runner.events):
            for event in action_runner.events:
                event.publish()

            action_runner.events = []

        return action_runner

    @scoped_session
    def _scoped(self, params):
        return self.call(params)

    def call(self):
        raise NotImplementedError
