import typing as t
import functools
from abc import ABC, abstractmethod

from .type_aliases import ViewType, ViewHint, ToRender, Bot, Message, Query
from .utils import get_trimmed_command
from .storage.base import AbstractStorage
from .views import TextView


class AbstractBotInterface(ABC):
    """ Base interface for all used adaptors, both sync and async """
    @abstractmethod
    def command_handler(self, command: str):
        pass

    @abstractmethod
    def action_handler(self, action: t.Optional[str] = None):
        pass

    @abstractmethod
    def start(self):
        pass


class AbstractBot(AbstractBotInterface):
    """ This class implements mapping handlers to its identifiers
        via decorators (and getting handlers back by protected methods) 
        No IO ops are performed, so both sync and async adaptors can use it """
    def __init__(self):
        self._command_handlers: t.Dict[str, t.Callable] = {}
        self._action_handlers: t.Dict[str, t.Callable] = {}
        self._views: t.Dict[str, ViewType] = {}

    def command_handler(self, command: str):
        def wrapper(handler: t.Callable):
            trimmed_command = get_trimmed_command(command)
            self._command_handlers[trimmed_command] = handler 
            return handler 
        return wrapper

    def action_handler(self, action: t.Optional[str] = None):
        def wrapper(handler: t.Callable):
            action_name = action or handler.__name__
            self._action_handlers[action_name] = handler
            return handler
        return wrapper

    def register_views(self, views: t.Iterable[ViewType]) -> None:
        for view_t in views:
            view_name = view_t.__name__
            self._views[view_name] = view_t

    def _get_command_handler(self, 
                             command: str) -> t.Optional[t.Callable]:
        return self._command_handlers.get(command, None)

    def _get_bounded_message_handler(
                    self, 
                    view_name: str) -> t.Optional[t.Callable]:
        view_t = self._views.get(view_name)
        if issubclass(view_t, TextView):
            view = view_t
            return functools.partial(view_t.on_message, view)

    def _get_bounded_action_handler(
                    self, 
                    action_name: str) -> t.Optional[t.Callable]:
        view_t, action = action_name.split(":")
        view_t = self._views.get(view_t, None)
        if view_t:
            method = self._action_handlers.get(action, None)
            if method:
                view = view_t()
                return functools.partial(method, view)

    def _validate_view(self, view: ViewHint) -> t.Optional[str]:
        """ Check whether view is in registered views. 
            Returns its string name or None otherwise """
        if not isinstance(view, str):
            try:
                view = view.__name__
            except AttributeError:
                pass 
        if view in self._views:
           return view
        # Consider logging here
        print(f"View was not found: `{view}`. "
              f"It is most likely that the view was not registered "
              f"via `register_views`")


class AbstractBotAdaptor(AbstractBot, t.Generic[Bot, Message, Query]):
    """ This class provides methods to dispatch messages 
        (commands, messages, queries) to corresponding sync handlers 

        To keep the code and inheritance schema simple, it also takes
        care of handling results, sending it and accessing storage 
        (instead of separate class for each) 

        So, all components required to work in a sync manner"""
    def __init__(self, bot: Bot, storage: AbstractStorage):
        self._bot = bot
        self._storage = storage 
        super().__init__()

    def _dispatch_command(
                self, 
                command: str, 
                message: Message) -> t.Optional[ToRender]:
        handler = self._get_command_handler(command)
        if handler:
            return handler(message)

    def _dispatch_message(
                self, 
                current_view: str, 
                message: Message) -> t.Optional[ToRender]:
        handler = self._get_bounded_message_handler(current_view)
        if handler:
            return handler(message) 
            
    def _dispatch_action(
                self, 
                action: str, 
                query: Query) -> t.Optional[ToRender]:
        handler = self._get_bounded_action_handler(action)
        if handler:
            return handler(query) 

    def _handle_command(self, 
                        user_id: int, 
                        command: str, 
                        message: Message) -> None:
        result = self._dispatch_command(command, message)
        self._render(user_id, result)

    def _handle_message(self, user_id: int, message: Message) -> None:
        current_view = None
        with self._storage.select_user(user_id) as user:
            current_view = user.get_current_view()
        # if not current_view ?
        if not current_view:
            return # we should have some defaults I guess
        result = self._dispatch_message(current_view, message)
        self._render(user_id, result)

    def _handle_action(self, user_id: int, action: str, query: Query) -> None:
        result = self._dispatch_action(action, query)
        self._render(user_id, result)

    def _render(self, to_user: int, render: t.Optional[ToRender]) -> None:
        # Scip if nothing to render
        if not render:
            return
        # Just send text message, don't update state
        elif isinstance(render, str):
            pass
        # Send message and update state
        else:
            view = self._validate_view(render.view)
            if view:
                with self._storage.select_user(to_user) as user:
                    user.set_current_view(view)
                    # send message
