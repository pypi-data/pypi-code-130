import asyncio
import atexit
import logging
import socket
import threading
from _queue import Empty
from queue import Queue
from time import sleep
from typing import Optional
from urllib.error import HTTPError

import requests


class Nelo2Exception(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Nelo2LoggingHandler(logging.Handler):
    def __init__(self, project_name: str, project_version: str, end_point: str, retry: int,
                 host: str = None, timeout: int = None, level: int = logging.NOTSET,
                 default_header: dict = None):
        super().__init__(level)
        self.project_name = project_name
        self.project_version = project_version
        self.host = host or socket.gethostname()
        self.end_point = end_point
        self.retry = retry or 2
        self.default_header = default_header
        self.timeout = timeout or 4
        self.session: requests.Session = requests.Session()

    def emit(self, record: logging.LogRecord) -> None:
        body = {
            'projectName': self.project_name,
            'projectVersion': self.project_version,
            'body': self.format(record),
            'host': self.host,
            'logLevel': record.levelname
        }

        for _ in range(self.retry):
            try:
                res = self.session.post(self.end_point, json=body, timeout=self.timeout, headers=self.default_header,
                                        verify=False)
                res.raise_for_status()
                break
            except Exception as e:
                print(e)
                # self.handleError(record)


signal_to_threads = threading.Event()
registered_threads: list[threading.Thread] = []


class AsyncNelo2LoggingHandler(logging.Handler):
    def __init__(self, project_name: str, project_version: str, end_point: str,
                 host: str = None, loop: asyncio.AbstractEventLoop = None,
                 timeout: int = None, level: int = logging.NOTSET, default_header: dict = None):
        super().__init__(level)
        self.project_name = project_name
        self.project_version = project_version
        self.host = host or socket.gethostname()
        self.end_point = end_point
        self.default_header = default_header
        self.timeout = timeout or 10
        self._queue = Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = loop
        # self._session: Optional[aiohttp.ClientSession] = None
        self._session: requests.Session = requests.Session()

        self.thread = threading.Thread(target=self.run, daemon=True)
        registered_threads.append(self.thread)
        self.thread.start()

    def run(self):
        while True:
            req_body = []
            try:
                for _ in range(20):
                    r = self._queue.get(timeout=0.001)
                    req_body.append({
                        'projectName': self.project_name,
                        'projectVersion': self.project_version,
                        'body': self.format(r),
                        'host': self.host,
                        'logLevel': r.levelname
                    })
            except Empty as e:
                pass

            if len(req_body) > 0:
                res = self._session.post(self.end_point, json=req_body, timeout=self.timeout, headers=self.default_header,
                                         verify=False)
                try:
                    res.raise_for_status()
                except HTTPError as e:
                    print(res)

                req_body.clear()

            if signal_to_threads.is_set() and self._queue.empty():
                break

    def emit(self, record: logging.LogRecord):
        self._queue.put(record)


@atexit.register
def signal_threads():
    print('signaling threads to stop')
    signal_to_threads.set()
    for _ in range(5):
        for t in registered_threads:
            t.join()
            break
        sleep(1)
