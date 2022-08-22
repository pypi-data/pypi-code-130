#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``common`` module for backend tests."""

from vmcp.osc.backend.typing import BackendType
from vmcp.osc import OSC


def wait_for_shutdown(backend: BackendType):
    """Wait until ``osc4py3`` is shut down completely.

    Args:
        backend (BackendType):
            Backend module.

    """
    def is_terminated(backend: BackendType) -> bool:
        """Return whether ``osc4py3`` is shutting down.

        Args:
            backend (BackendType):
                Backend module.

        Returns:
            bool:
                ``True`` if is shutting down, otherwise ``False``.

        """
        terminated = False
        try:
            backend.globdisp()
        except RuntimeError:
            terminated = True
        finally:
            return terminated  # pylint: disable=lost-exception
    while not is_terminated(backend):
        pass
    while len(backend.all_dispatchers) > 0:
        for dispacher in tuple(backend.all_dispatchers.values()):
            dispacher.terminate()


def test_run(backend: BackendType):
    """Test run.

    Args:
        backend (BackendType):
            Backend module.

    """
    try:
        osc = OSC(backend)
        with osc.open():
            osc.run()
    finally:
        osc.close()
        wait_for_shutdown(backend)
