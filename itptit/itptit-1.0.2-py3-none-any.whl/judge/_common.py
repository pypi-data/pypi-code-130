from ..common import (
    format as _format,
    cursor as _cursor,
    stdout as _stdout
)
from threading import Lock


class Cursor:
    def __init__(self, cur_line):
        self.cur_line = cur_line

    def jumpto(self, dest, start_index):
        delta = dest - self.cur_line
        self.cur_line = dest
        if delta > 0:
            _cursor.down(delta)
        elif delta < 0:
            _cursor.up(-delta)
        _stdout.print('\r')
        _cursor.next(start_index)
        _cursor.del_line()


class SynAssets:
    def __init__(self, assets):
        self.lock = Lock()
        self.assets = assets


class TestCaseInfo:
    def __init__(self, order, testname, input_file_path, output_file_path):
        self.order = order
        self.testname = testname
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.display_start_index = None


class JudgeResult:
    def __init__(self, testcase_info: TestCaseInfo, result=None, cost_time=None, output=None):
        self.testcase_info = testcase_info
        self.result = result
        self.cost_time = cost_time
        self.output = output

    def get(self):
        return self.result == 'AC'

    def __str__(self):
        if self.result == 'WA':
            return _format.formating('Wrong answer (WA).', _format.RED)
        if self.result == 'IR':
            return _format.formating('Invalid Return (IR).', _format.RED)
        if self.result == 'RTE':
            return _format.formating('Run Time Error (RTE).', _format.RED)
        if self.result == 'TLE':
            return _format.formating('Time Limit Exceeded (TLE).', _format.RED)
        if self.result == 'AC':
            return _format.formating('Accepted (AC) in %.3fs.' % self.cost_time, _format.GREEN)
        return _format.formating('Unknown.', _format.YELLOW)
