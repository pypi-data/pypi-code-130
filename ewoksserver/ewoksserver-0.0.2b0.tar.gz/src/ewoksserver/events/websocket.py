from datetime import datetime
import threading

import flask
from flask import copy_current_request_context
from flask_socketio import SocketIO
from flask_socketio import emit

from .ewoks_events import reader_context

fversion = tuple(map(int, flask.__version__.split(".")))[:2]
if fversion < (2, 2):
    from flask.globals import _app_ctx_stack
else:
    _app_ctx_stack = None


def copy_current_app_context(fn):
    if _app_ctx_stack is None:
        return fn

    app_context = _app_ctx_stack.top

    def wrapper(*args, **kwargs):
        with app_context:
            return fn(*args, **kwargs)

    return wrapper


def add_events(socketio: SocketIO):
    socketio.on("connect")(connect)
    socketio.on("disconnect")(disconnect)


def connect():
    _EMITTER.connect()


def disconnect():
    _EMITTER.disconnect()


def is_running():
    return _EMITTER.is_running()


class EwoksEventEmitter:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread = None
        self._counter = 0

    def connect(self):
        self._counter += 1
        self.start()

    def disconnect(self):
        self._counter = max(self._counter - 1, 0)
        if self._counter == 0:
            self.stop(timeout=3)

    def is_running(self):
        return self._thread is not None

    def start(self):
        if self._thread is not None:
            return

        # Flask context's have thread affinity
        @copy_current_request_context
        @copy_current_app_context
        def main():
            self._main()

        self._stop_event.clear()
        self._thread = threading.Thread(target=main, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = None):
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=timeout)

    def _main(self):
        try:
            with reader_context() as reader:
                if reader is None:
                    return
                starttime = datetime.now().astimezone()
                for event in reader.wait_events(
                    starttime=starttime, stop_event=self._stop_event
                ):
                    if self._stop_event.is_set():
                        break
                    emit("Executing", event, broadcast=True)
        finally:
            self._thread = None


_EMITTER = EwoksEventEmitter()
