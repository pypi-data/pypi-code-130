"""Plugin module."""

from copy import deepcopy
from threading import Lock
from typing import Any, Coroutine, Dict, Union

setup_lock = Lock()


AsyncHook = Union[Any, Coroutine, None]


class EmbedMiddleware:
    """Embed middleware."""

    __slots__ = 'app',

    plugin = None

    def __init__(self, app):
        """Init."""
        self.app = app

    def __call__(self, scope, receive, send) -> None:
        """Override __call__."""
        return self.plugin.process(scope, receive, send, app=self.app)


class MetaPlugin(type):
    """Meta plugin."""

    def __new__(mcs, alias, bases, params):
        """Override new."""
        cls = super().__new__(mcs, alias, bases, params)
        if bases and not getattr(cls, 'alias'):
            raise RuntimeError(f'Invalid plugin alias {cls}')
        return cls


class Plugin(metaclass=MetaPlugin):
    """Plugin."""

    alias: str = None

    options: Dict = dict()

    middleware: AsyncHook = None
    on_startup: AsyncHook = None
    on_shutdown: AsyncHook = None

    def __init__(self, app=None, **settings):
        """Init."""
        self.app = app
        self.options.update(settings)  # noqa
        if self.app:
            self.setup(app)

    def register(self, app) -> None:
        """Store in plugin registry."""
        with setup_lock:
            if not hasattr(app, '_plugin_store'):
                app._plugin_store = type('Plugins', (object,), {})
            setattr(app._plugin_store, self.alias, self)

    def __call__(self, app, **settings):
        """Override __call__."""
        self.app = app
        self.register(app)

        _options = deepcopy(self.options)
        _options.update(settings)

        self.options = type(  # noqa
            f'{self.alias.title()}Config',
            (object,),
            _options,
        )

        return type(
            f'{self.alias.title()}Middleware',
            (EmbedMiddleware,),
            {'plugin': self},
        )

    def setup(self, app, **kwargs):  # noqa
        """Setup."""
        app_middleware = self(app, **kwargs)
        self.app.add_middleware(app_middleware)

    def process(self, scope, receive, send, app=None):
        """Process."""
        app = app or self.app
        try:
            if scope['type'] == 'lifespan':
                return self.lifespan(scope, receive, send, app)

            return self.middleware(scope, receive, send, app)

        except Exception as exc:
            return self.exception(exc, scope, receive, send, app)

    def lifespan(self, scope, receive, send, app):
        """Lifespan loopback."""
        hook = {
            'lifespan.startup': self.startup,
            'lifespan.shutdown': self.shutdown,
        }

        async def reply_receive():  # noqa
            message = await receive()
            if message['type'] in hook.keys():
                await hook[message['type']](scope)  # noqa
            return message

        return app(scope, reply_receive, send)

    async def middleware(self, scope, receive, send, app):  # noqa
        """Middleware."""
        return await app(scope, send, receive)

    async def startup(self, scope):   # noqa
        """Startup."""
        pass

    async def shutdown(self, scope):  # noqa
        """Shutdown."""
        pass

    def exception(self, exc, scope, receive, send, app):  # noqa
        """Exception."""
        raise exc
