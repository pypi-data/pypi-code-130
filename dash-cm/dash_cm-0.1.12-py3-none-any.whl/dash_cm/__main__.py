import logging
import signal
import subprocess

import treefiles as tf


def serve():
    # to stop: `netstat -tulpn | grep LISTEN |grep 3000` to get the pid
    # and `kill -9 <pid>`

    def handler(signum, frame):
        print("\nExisting server")

    signal.signal(signal.SIGINT, handler)

    subprocess.call(["serve", "-s", tf.f(__file__) / "build"])


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    serve()
