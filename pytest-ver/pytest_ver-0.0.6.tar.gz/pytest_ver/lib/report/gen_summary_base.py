from ..requirements import Requirements


# -------------------
## Common functions for Summary reports
class GenSummaryBase:
    # -------------------
    ## constructor
    def __init__(self):
        ## holds the summary info
        self._summary = None
        ## holds reference to the Requirements object
        self._requirements = None

    # -------------------
    ## initialization
    #
    # @return None
    def _init(self):
        self._requirements = Requirements()
        self._requirements.load()

    # -------------------
    ## count requirements: failing, passing, invalid
    #
    # @param total           total number of requirements
    # @param report_invalid  callback function that prints a message that a requirement id is invalid
    # @return tuple: failing, passing, invalid
    def _count_requirements(self, total, report_invalid):
        num_failing = 0
        num_passing = 0
        num_invalid = 0
        for reqid, item in self._summary['reqids'].items():
            if item['result'] == 'FAIL':
                num_failing += 1
            else:
                num_passing += 1

            if self._requirements.is_found and not self._requirements.is_valid(reqid):
                num_invalid += 1
                report_invalid(reqid)

        num_missing = total - (num_passing + num_failing) + num_invalid
        return num_failing, num_passing, num_invalid, num_missing

    # -------------------
    ## count the passing/failing protocols
    #
    # @return tuple: failing, passing
    def _count_protocols(self):
        num_failing = 0
        num_passing = 0
        for reqids, item in self._summary['protoids'].items():
            if item['result'] == 'FAIL':
                num_failing += 1
            else:
                num_passing += 1

        return num_failing, num_passing

    # -------------------
    ## calculate the percentage count is of total
    #
    # @param count  the current count
    # @param total  the current total
    # @return formatted string with percent
    def _pct(self, count, total):
        if total == 0:
            pct = 0
        else:
            pct = round((count * 100.0) / total, 1)
        return f'{pct: >6}%'
