from io import (
    BytesIO,
    TextIOWrapper
)
from sys import settrace
from threading import Thread
from time import time
from ..common.exceptions import (
    JudgeException,
    RunTimeError,
    InvalidReturn,
    TimeLimitExceeded
)
from subprocess import run as systemrun
from ..common import (
    format as _format,
    stdout as _stdout
)
from ._common import (
    TestCaseInfo,
    JudgeResult,
    SynAssets
)
from platform import system as osname

class StoppableThread(Thread):
    def __init__(
        self,
        group=None,
        target=None,
        name=None,
        args=(),
        kwargs=None,
        *,
        daemon=None
    ):
        super().__init__(group, target, name, args=args, kwargs=kwargs, daemon=daemon)
        self.exception = None
        self.__killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self._run
        Thread.start(self)

    def _run(self):
        settrace(self.globaltrace)
        try:
            self.__run_backup()
        except JudgeException as e:
            self.exception = e
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        return None

    def localtrace(self, frame, event, arg):
        if self.__killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.__killed = True


class TestCaseRunner(StoppableThread):
    def __init__(
        self,
        command,
        judge_result: JudgeResult
    ):
        super().__init__(daemon=True)
        self.command = command
        self.judge_result = judge_result
        self.exeption = None

    def _run_process(self):
        start_time = time()
        process = systemrun(self.command, stdout=-1)
        end_time = time()
        self.judge_result.cost_time = end_time - start_time
        if process.returncode != 0:
            raise RunTimeError()
        with TextIOWrapper(BytesIO(process.stdout)) as outstream:
            self.judge_result.output = outstream.read()

    def run(self):
        settrace(self.globaltrace)
        try:
            self._run_process()
        except JudgeException as e:
            self.exeption = e


class TestCaseManager(Thread):
    def __init__(
        self,
        judge,
        time_limit,
        solution_path,
        actualoutput_dir,
        testcase_queue: SynAssets,
    ):
        self.judge = judge
        self.stdcursor = self.judge.stdcursor
        self.time_limit = time_limit
        self.solution_path = solution_path
        self.actualoutput_dir = actualoutput_dir
        self.testcase_queue = testcase_queue
        self.judge_result = None
        self.runner = None
        super().__init__()

    def setup(
        self,
        testcase_info: TestCaseInfo
    ):
        self.testcase_info = testcase_info

        self.stdcursor.lock.acquire()
        self.stdcursor.assets.jumpto(
            testcase_info.order, testcase_info.display_start_index)
        _stdout.print(_format.formating('Judging...', _format.YELLOW))
        self.stdcursor.lock.release()

        self.language = self.solution_path[self.solution_path.rfind('.') + 1:]

        if self.language == 'py':
            pyrun = 'py' if osname() == 'Windows' else 'python3'
            command = f'{pyrun} {self.solution_path} < {testcase_info.input_file_path}'
        elif self.language in ('c', 'cpp'):
            command = f'./judgingprocess < {testcase_info.input_file_path}'
        if osname() == 'Windows':
            command = f'cmd /c "{command}'
        if self.judge_result is not None:
            del self.judge_result
        if self.runner is not None:
            del self.runner
        self.judge_result = JudgeResult(testcase_info)
        self.runner = TestCaseRunner(command, self.judge_result)

    def _run_testcase(self):
        self.runner.start()
        if self.time_limit is None:
            self.runner.join()
        else:
            self.runner.join(self.time_limit)

        if self.runner.exeption is not None:
            raise self.runner.exeption
        if (
            self.time_limit is not None
            and (
                self.runner.judge_result.cost_time is None
                or
                self.runner.judge_result.cost_time > self.time_limit
            )
        ):
            self.runner.kill()
            raise TimeLimitExceeded()

        if (
            self.language == 'py' and self.judge_result.output.startswith(
                'Traceback')
            or
            self.language in ('c', 'cpp') and 'terminate called after throwing' in self.judge_result.output
        ):
            raise InvalidReturn()

    def run(self):
        while True:
            self.testcase_queue.lock.acquire()
            stop_flag = False
            if self.testcase_queue.assets:
                self.setup(self.testcase_queue.assets.pop())
            else:
                stop_flag = True
            self.testcase_queue.lock.release()
            if stop_flag:
                return
            try:
                self._run_testcase()
            except InvalidReturn:
                self.judge_result.result = 'IR'
            except RunTimeError:
                self.judge_result.result = 'RTE'
            except TimeLimitExceeded:
                self.judge_result.result = 'TLE'
            if self.judge_result.output is not None:
                self._check_result()
                if self.actualoutput_dir is not None:
                    with open(f'{self.actualoutput_dir}/{self.testcase_info.testname}.txt', 'w', encoding='utf-8') as actualoutput_file:
                        actualoutput_file.write(self.judge_result.output)
            self._report_result()

    def _check_result(self):
        with open(self.testcase_info.output_file_path, 'r', encoding='utf-8') as expected_outputfile:
            if self.judge_result.output.strip() == expected_outputfile.read().strip():
                self.judge_result.result = 'AC'
                self.judge.accnt += 1
            else:
                self.judge_result.result = 'WA'

    def _report_result(self):
        self.stdcursor.lock.acquire()
        self.stdcursor.assets.jumpto(
            self.testcase_info.order, self.testcase_info.display_start_index)
        _stdout.print(self.judge_result)
        self.stdcursor.lock.release()
