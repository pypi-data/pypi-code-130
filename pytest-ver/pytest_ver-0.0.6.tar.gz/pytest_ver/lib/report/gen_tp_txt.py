import os

from .gen_base_txt import GenBaseTxt
from .. import services
from ..result_summary import ResultSummary


# -------------------
## Generates a Test Protocol report in text format
class GenTpTxt(GenBaseTxt):
    # -------------------
    ## constructor
    #
    # @param protocols   the data to use
    # @param do_results  generate results or not
    def __init__(self, protocols, do_results=True):
        super().__init__()
        ## holds protocol inforation
        self._protocols = protocols
        ## holds flag to generate results (for TP report), or not (for TP doc)
        self._do_results = do_results

        if self._do_results:
            fname = services.cfg.tp_report_fname
        else:
            fname = services.cfg.tp_protocol_fname

        ## holds path to the ouput file
        self._path = os.path.join(services.cfg.outdir, f'{fname}.txt')

    # -------------------
    ## generate the report
    #
    # @return None
    def gen(self):
        # TODO add detailed flag

        if self._do_results:
            services.logger.start('report: TP with results (text)')
        else:
            services.logger.start('report: TP without results (text)')
        # uncomment to debug:
        # services.logger.dbg(f'protocols: {json.dumps(self._protocols, indent=2)}')

        fp = open(self._path, 'w')
        self._gen_test_run_details(fp)
        if self._do_results:
            self._gen_title(fp, 'Test Protocols with results')
        else:
            self._gen_title(fp, 'Test Protocols')

        for proto_id, protocol in self._protocols.items():
            fp.write(f'==== protocol: {proto_id} {protocol["desc"]}\n')
            self._gen_protocol_info(fp, protocol)

            stepno = 0
            for step in protocol['steps']:
                stepno += 1
                fp.write(f'     Step {stepno: <3}: {step["desc"]}\n')
                self._gen_step_info(fp, step)

                # default is a passed, and empty result
                self._gen_step_results(fp, step)

            fp.write(f'\n')
        fp.close()

    # -------------------
    ## generate the overall protocol information
    #
    # @param fp        the file to write to
    # @param protocol  the protocol data
    # @return None
    def _gen_protocol_info(self, fp, protocol):
        fp.write(f'     location: {protocol["location"]}\n')

    # -------------------
    ## generate the overall step information
    #
    # @param fp     the file to write to
    # @param step   the step data
    # @return None
    def _gen_step_info(self, fp, step):
        if self._do_results:
            fp.write(f'       > dts          : {step["dts"]}\n')
        else:
            fp.write(f'       > dts          : \n')

    # -------------------
    ## generate the results for the given step
    #
    # @param fp     the file to write to
    # @param step   the step data
    # @return None
    def _gen_step_results(self, fp, step):
        rs = ResultSummary()
        rs.passed()

        for res in step['results']:
            rs = ResultSummary()
            rs.load(res)
            if rs.result == 'FAIL':
                break

        if self._do_results:
            fp.write(f'       > result       : {rs.result}\n')
            fp.write(f'       > actual       : {rs.actual_formatted}\n')
            fp.write(f'       > actual raw   : {rs.actual}\n')
        else:
            fp.write(f'       > result       : \n')
            fp.write(f'       > actual       : \n')
            fp.write(f'       > actual raw   : \n')
        fp.write(f'       > expected     : {rs.expected_formatted}\n')
        fp.write(f'       > expected raw : {rs.expected}\n')
        fp.write(f'       > reqids       : {rs.reqids}\n')
        fp.write(f'       > location     : {rs.location}\n')

        self._gen_step_comments(fp, step)

    # -------------------
    ## generate the comments for the given step
    #
    # @param fp     the file to write to
    # @param step   the step data
    # @return None
    def _gen_step_comments(self, fp, step):
        if self._do_results:
            for comment in step['comments']:
                fp.write(f'       > Note         : {comment}\n')
