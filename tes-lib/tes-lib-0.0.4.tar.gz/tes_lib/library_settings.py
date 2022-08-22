"""
The library settings and state
"""
import time
from multiprocessing import Queue, Pipe, Process
import requests
import logging

from .errors import TesLibError
from .test_event_store import event_store_run_loop
from .add_event_web_server import run_webserver
from .messages import ShutdownMessage, ResetMessage
from .constants import DEFAULT_PORT, DEFAULT_IP


class _TesLib:
    def __init__(self):
        self.queue = Queue()
        self.parent_conn, self.child_conn = Pipe()

        self.ip_address = DEFAULT_IP
        self.port = DEFAULT_PORT

        self.event_store_process = None
        self.webserver_process = None

        self._initialised = False

    @staticmethod
    def wait_for_webserver(ip_address: str, port: int):
        """Wait for the webserver to be up and ready

        :param ip_address: The ip_address the webserver is listening
        :param port: The port the webserver is listening on
        :return: None
        """
        timeout = 5
        url = f"http://{ip_address}:{port}/ready"
        for _ in range(timeout):
            try:
                response = requests.get(url=url)
                # Works fine pylint just doesn't understand what's going on
                # pylint: disable=no-member
                if response.status_code == requests.codes.ok:
                    return
            except requests.exceptions.ConnectionError:
                # Webserver may not be ready to listen yet - this is what we're trying to check
                # so is expected behaviour
                pass

            time.sleep(1)

        raise RuntimeError(
            "Failed to initialise library - no response from add event webserver before timeout"
        )

    def initialise(self, ip_address: str, port: int):
        """Initialise the library

        :param ip_address: The ip_address the webserver should  listen on
        :param port: The port the webserver should listen on
        :return: None
        """
        if self._initialised:
            return

        self.ip_address = ip_address
        self.port = port

        self.event_store_process = Process(
            target=event_store_run_loop, args=(self.queue, self.child_conn)
        )
        self.event_store_process.start()
        self.webserver_process = Process(target=run_webserver, args=(self.queue, ip_address, port))
        self.webserver_process.start()

        self.wait_for_webserver(ip_address, port)

        self._initialised = True

    def reset(self, timeout=5):
        """Reset the event store ready for the next test run

        :param timeout: The amount of time to give the event store to reset
        :return: None
        """
        if not self._initialised:
            return

        self.queue.put(ResetMessage())

        # pylint: disable=cyclic-import,import-outside-toplevel
        from .event_helpers import wait_for_response

        try:
            _ = wait_for_response("Reset test event store", self.parent_conn, timeout=timeout)
        except TesLibError:
            # If we don't get a response reset the library
            logging.error("No response from event store on reset - restarting processes")

            self.cleanup()
            self.initialise(self.ip_address, self.port)

    def cleanup(self):
        """Cleanup the library

        :return: None
        """
        if not self._initialised:
            return

        self.queue.put(ShutdownMessage())
        self.event_store_process.join(timeout=3)
        self.webserver_process.terminate()
        self.webserver_process.join(timeout=3)

        self._initialised = False


class _TesLibInstance:

    INSTANCE = None

    @staticmethod
    def get_instance():
        """Get an instance of the TesLib class

        :return: TesLib instance
        """
        if _TesLibInstance.INSTANCE is None:
            _TesLibInstance.INSTANCE = _TesLib()
        return _TesLibInstance.INSTANCE


def initialise(ip_address: str = DEFAULT_IP, port: int = DEFAULT_PORT):
    """Initialise the library - this will start the event store and webserver processes. Each call
    of initialise should be paired with a call to cleanup.

    Calling this function multiple times without calling cleanup between will have no effect

    :param ip_address: The IP address to be used by the add event webserver
    :param port: The port to be used by the add event webserver
    :return: None
    """
    _TesLibInstance.get_instance().initialise(ip_address, port)


def reset_event_store():
    """Reset the test event store removing all event. This function will call cleanup followed by
    initialise if it fails to reset the event store.

    Calling this function without first calling initialise will have no effect

    :return: None
    """
    _TesLibInstance.get_instance().reset()


def cleanup():
    """Cleanup the library - this will stop the event store and webserver processes

    Calling this function multiple times without calling initialise between will have no effect

    :return: None
    """
    _TesLibInstance.get_instance().cleanup()
