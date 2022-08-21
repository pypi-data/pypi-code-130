import datetime

from .. import services


# -------------------
## Base class for generating a text file
class GenBaseTxt:

    # -------------------
    ## constructor
    def __init__(self):
        pass

    # -------------------
    ## generate test run information
    #
    # @param fp  the file pointer to write to
    # @return None
    def _gen_test_run_details(self, fp):
        self._gen_title2(fp, 'Test Run Details')
        fp.write(f"{'Test Run Type': <20}: {services.cfg.test_run_type}\n")
        fp.write(f"{'Test Run ID': <20}: {services.cfg.test_run_id}\n")
        dts = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime(services.cfg.dts_format)
        fp.write(f"{'Document Generated': <20}: {dts}\n")

        services.cfg.page_info.report(fp)
        fp.write('\n')

    # -------------------
    ## generate title
    #
    # @param fp     the file to write to
    # @param title  the title to draw
    # @return None
    def _gen_title(self, fp, title):
        self._gen_title2(fp, title)
        fp.write('\n')

    # -------------------
    ## generate title lines
    #
    # @param fp     the file to write to
    # @param title  the title to draw
    # @return None
    def _gen_title2(self, fp, title):
        fp.write(f'{title}\n')
        fp.write(f"{'-' * len(title)}\n")
