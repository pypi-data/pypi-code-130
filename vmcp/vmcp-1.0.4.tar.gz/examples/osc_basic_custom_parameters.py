#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Basic OSC protocol example with custom receiving parameters."""

from typing import Any
from vmcp.osc import OSC
from vmcp.osc.typing import Message
from vmcp.osc.backend.osc4py3 import as_comthreads as backend
from vmcp.osc.backend.osc4py3._as_comthreads import (
    ARG_DATAUNPACK,
    ARG_READERNAME
)

LISTENING: bool = True


def received(*args: Any):
    """Receive transmission."""
    global LISTENING  # pylint: disable=global-statement
    print(args)
    LISTENING = False


try:
    osc = OSC(backend)
    with osc.open():
        # Receiver channel
        in1 = osc.create_receiver("127.0.0.1", 39539, "receiver1")
        in1.register_handler(
            "/test/one",
            received,
            ARG_READERNAME + ARG_DATAUNPACK  # Default: ARG_DATAUNPACK
        )
        in1.open()
        # Sender channel
        out1 = osc.create_sender("127.0.0.1", 39539, "sender1").open()
        out1.send(Message("/test/one", ",sif", ["first", 672, 8.871]))
        # Processing
        while LISTENING:
            osc.run()
except KeyboardInterrupt:
    print("Cancheled.")
finally:
    osc.close()
