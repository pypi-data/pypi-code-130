import logging
import signal
import subprocess

import treefiles as tf


def serve_local():
    """
    Start local server
    """
    # to stop process using port: `netstat -tulpn | grep LISTEN |grep 3000` to get the pid
    # and `kill -9 <pid>`

    def handler(signum, frame):
        print("\nExisting server")

    signal.signal(signal.SIGINT, handler)
    subprocess.call(["serve", "-s", tf.f(__file__) / "build"])


log = logging.getLogger(__name__)
