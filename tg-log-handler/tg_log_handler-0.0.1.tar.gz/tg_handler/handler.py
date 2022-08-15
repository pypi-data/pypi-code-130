import logging
from threading import RLock, Thread
from time import sleep

import requests
from retry import retry
from tg_handler.buffer import Buffer

logger = logging.getLogger(__name__)


FLUSH_INTERVAL = 5
API_HOST = 'api.telegram.org'
API_URL = f'https://{API_HOST}/bot{{bot_token}}/sendMessage?chat_id={{chat_id}}&parse_mode=HTML'
RETRY_COOLDOWN_TIME = 60
MAX_RETRYS = 20
RETRY_BACKOFF_TIME = 5
# максимальный допустимый размер - 4096, мы берем буфер на всякий случай
MAX_MESSAGE_SIZE = 4000
TOO_MANY_REQUESTS = 429
MAX_BUFFER_SIZE = 10**16


class TelegramLoggingHandler(logging.Handler):
    def __init__(self, bot_token, chat_id, level=logging.NOTSET):
        super().__init__(level)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self._buffer = Buffer(MAX_BUFFER_SIZE)
        self._stop_signal = RLock()
        self._writer_thread = None
        self._start_writer_thread()

    @retry(requests.exceptions.RequestException,
           tries=MAX_RETRYS,
           delay=RETRY_COOLDOWN_TIME,
           backoff=RETRY_BACKOFF_TIME,
           logger=logger)
    def write(self, message):
        url = API_URL.format(bot_token=self.bot_token,
                             chat_id=self.chat_id)
        response = requests.post(url, data={'text': message})

        response.raise_for_status()
        if response.status_code == requests.codes.too_many_requests:
            raise requests.exceptions.RequestException(
                "Превышено максимальное количество запросов к серверу")

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self._buffer.write(message)

    def close(self):
        with self._stop_signal:
            self._writer_thread.join()

    def _write_manager(self):
        while True:
            lock_status = self._stop_signal.acquire(blocking=False)
            if not lock_status:
                break
            else:
                self._stop_signal.release()

            sleep(FLUSH_INTERVAL)
            message = self._buffer.read(MAX_MESSAGE_SIZE)
            if message != '':
                self.write(message)

    def _start_writer_thread(self):
        self._writer_thread = Thread(target=self._write_manager)
        self._writer_thread.daemon = True
        self._writer_thread.start()
