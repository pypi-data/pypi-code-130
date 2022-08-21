import json
import os
import re

import jsmin

from pytest_ver.lib.report.page_info import PageInfo
from . import services


# -------------------
## Holds configuration functions and globals
class Cfg:
    # -------------------
    ## constructor
    def __init__(self):
        # --- Public - default settings
        ## holds path to cfg file
        self.cfg_path = 'cfg.json'
        ## holds path to output directory
        self.outdir = 'out'

        ## holds storage type
        self.storage_type = 'dev'
        ## holds run type: one of formal, dryrun, dev
        self.test_run_type = 'dev'
        ## holds run id
        self.test_run_id = 'dev-001'
        ## holds format to use for DTS
        self.dts_format = "%Y-%m-%d %H:%M:%S %Z"
        ## holds page info e.g. headers and footers
        self.page_info = PageInfo()
        ## holds current test name
        self.test_script = 'unknown'
        ## holds path to the requirements json file
        self.reqmt_json_path = None

        ## test protocol file name - no results
        self.tp_protocol_fname = 'test_protocol'
        ## test report file name - with results
        self.tp_report_fname = 'test_report'

    # -------------------
    ## initialize - step1
    # read cfg json file
    #
    # @return None
    def init(self):
        if 'PYTEST_VER_CFG' in os.environ:
            self.cfg_path = os.environ['PYTEST_VER_CFG']

        self._read_ini()

        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)

    # -------------------
    ## initialize - step2
    # get the current test name
    #
    # @return None
    def init2(self):
        self.test_script = 'unknown'
        if 'PYTEST_CURRENT_TEST' in os.environ:
            # eg.  ver/test_sample_ver1.py
            m = re.search(r'test_(\w+)\.py::(\w+)', os.getenv('PYTEST_CURRENT_TEST'))
            if m:
                self.test_script = m.group(1)

    # -------------------
    ## report configuration to the log
    #
    # @return None
    def report(self):
        services.logger.start('Cfg:')
        services.logger.line(f"  {'Cfg path': <20}: {self.cfg_path}")
        services.logger.line(f"  {'Output Dir': <20}: {self.outdir}")
        services.logger.line(f"  {'Storage Type': <20}: {self.storage_type}")
        services.logger.line(f"  {'Test Run ID': <20}: {self.test_run_id}")
        services.logger.line(f"  {'Test Name': <20}: {self.test_script}")
        services.logger.line(f"  {'Req. json path': <20}: {self.reqmt_json_path}")
        if services.iuvmode:  # pragma: no cover
            services.logger.line(f"  {'IUV mode': <20}: {services.iuvmode}")

        services.logger.line('')

    # -------------------
    ## read the cfg json file
    # set attributes in this class based on content
    #
    # @return None
    def _read_ini(self):
        if not os.path.isfile(self.cfg_path):
            services.logger.warn(f'{self.cfg_path} not found')
            return

        # load json file
        with open(self.cfg_path, 'r') as fp:
            cleanj = jsmin.jsmin(fp.read())
            j = json.loads(cleanj)

        # override and/or add to available attributes
        for key, value in j.items():
            if key == 'tp_report':
                self.page_info.init_tp_report(value)
            elif key == 'tp_protocol':
                    self.page_info.init_tp_protocol(value)
            elif key == 'trace':
                self.page_info.init_trace(value)
            elif key == 'summary':
                self.page_info.init_summary(value)
            else:
                setattr(self, key, value)
