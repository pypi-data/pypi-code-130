import logging
import signal
from threading import Thread
from time import sleep
from typing import List

from django.core.management.base import BaseCommand

from simpleworker.scheduler import SimpleScheduler
from simpleworker.simple_worker import SimpleWorker

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    should_exit: bool = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            action='append',
            default=[],
            dest='queues',
        )
        parser.add_argument(
            '--with_cron',
            action='store_true',
            default=False,
            dest='with_cron',
        )
        parser.add_argument(
            '--max_processed_tasks',
            action='store',
            default=0,
            dest='max_processed_tasks',
        )

    def run_solo(self, queues: List[str], max_processed_tasks: int):
        worker = SimpleWorker(queues, max_processed_tasks)
        worker.run()

    def start_thread(self, function) -> Thread:
        thread = Thread(target=function)
        thread.daemon = True
        thread.start()
        return thread

    def run_with_cron(self, queues: List[str], max_processed_tasks: int):
        scheduler = SimpleScheduler().get_background_scheduler()
        scheduler.start()
        worker = SimpleWorker(queues, max_processed_tasks)

        # noinspection PyProtectedMember
        threads: List[Thread] = [
            self.start_thread(worker.run),
            scheduler._thread,
        ]

        def shutdown(signum, frame):
            logger.info(f'Exit requested signal={signum}')
            self.should_exit = True

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        while not self.should_exit:
            for thread in threads:
                if not thread.is_alive():
                    raise RuntimeError('Thread exited')
                sleep(1)

    def handle(self, *args, **options):
        queues: List[str] = options['queues']
        with_cron = options['with_cron']
        max_processed_tasks = options['max_processed_tasks']

        if with_cron:
            self.run_with_cron(queues, max_processed_tasks)
        else:
            self.run_solo(queues, max_processed_tasks)
