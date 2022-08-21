import os

import pytest

from pytest_ver.lib.iuv.iuv import IUV
from . import services
from .cfg import Cfg
from .log.logger import Logger
from .log.logger_stdout import LoggerStdout
from .protocol import Protocol
from .report.report import Report
from .storage.storage import Storage
from .summary import Summary
from .trace_matrix import TraceMatrix
from .verifier import Verifier


# -------------------
## Holds the overall test harness
# initializes the services object
class PytestHarness:
    # -------------------
    ## constructor
    def __init__(self):
        services.harness = self

        if os.environ['iuvmode'] == 'True':  # pragma: no cover
            services.iuvmode = True
            ## holds the IUV object when needed
            self.iuv = IUV()
            self.iuv.init()

        ## hplds reference to the protocol object
        self.proto = None
        ## holds reference to the verifier object
        self.ver = None
        ## holds reference to the logger object
        self.logger = None

        services.logger = LoggerStdout()
        services.logger.init()
        self.logger = services.logger

    # -------------------
    ## initialize - once per invocation
    #
    # @return None
    def init(self):
        services.cfg = Cfg()
        services.cfg.init()

        # after cfg indicates where log files are stored, can use normal logger
        services.logger = Logger()
        services.logger.init()

        services.storage = Storage.factory()
        services.summary = Summary()
        services.trace = TraceMatrix()
        services.proto = Protocol()

        self.proto = services.proto
        self.ver = Verifier()
        self.logger = services.logger

        services.cfg.init2()
        services.cfg.report()

        services.proto.init()
        services.storage.init()
        if services.iuvmode:  # pragma: no cover
            self.iuv.init2()

    # -------------------
    ## terminate
    #
    # @return None
    def term(self):
        services.proto.term()
        services.trace.term()
        services.summary.term()
        services.storage.term()

    # -------------------
    ## run a report
    #
    # @return None
    def report(self):
        rep = Report()
        rep.report()

    # -------------------
    ## abort the run
    #
    # @return None
    def abort(self):
        services.logger.err('abort called')
        if services.iuvmode:  # pragma: no cover
            self.iuv.abort()
        else:
            pytest.exit('abort called')  # pragma: no cover
