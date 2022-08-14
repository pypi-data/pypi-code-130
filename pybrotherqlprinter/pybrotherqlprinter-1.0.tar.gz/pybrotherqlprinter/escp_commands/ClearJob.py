#!/usr/bin/env python3

from ._command import BrotherGenericCommand


class CmdClearJob(BrotherGenericCommand):

    """According to manual: In order to clear any jobs with errors remaining in
    printer, send 200 bytes of Invalid Command."""

    def __bytes__(self):
        return b"\x00" * 200
