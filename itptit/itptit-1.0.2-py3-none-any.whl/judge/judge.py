from io import (
    BytesIO,
    TextIOWrapper
)
from os import (
    listdir,
    makedirs,
    remove,
    system,
    cpu_count
)
from os.path import exists
from time import time
from ..common.exceptions import (
    MissingFileException,
    RunTimeError,
    CompileError,
    InvalidReturn,
    TimeLimitExceeded
)
from subprocess import (
    run as systemrun,
    PIPE,
    DEVNULL
)
from ..common import (
    format as _format
)

from ._thread import (
    StoppableThread,
    TestCaseManager
)

from ._common import (
    JudgeResult,
    SynAssets,
    TestCaseInfo,
    Cursor
)
from platform import system as osname


class _DEFAULT:
    TIME_LIMIT = None
    INPUT_EXTENSION = 'in'
    OUTPUT_EXTENSION = 'out'
    ACTUALOUTPUT_DIRECTORY = None
    JUDGE_IN_TURN = False
    try:
        NUMBER_OF_JUDGES = cpu_count()
    except:
        NUMBER_OF_JUDGES = 4


class _BaseJudge:
    def __init__(
        self,
        intestsuite_dir,
        outtestsuite_dir,
        solution_path,
        *,
        time_limit=_DEFAULT.TIME_LIMIT,
        input_extension=_DEFAULT.INPUT_EXTENSION,
        output_extension=_DEFAULT.OUTPUT_EXTENSION,
        actualout_dir=_DEFAULT.ACTUALOUTPUT_DIRECTORY
    ) -> None:

        self.intestsuite_dir = intestsuite_dir
        self.outtestsuite_dir = outtestsuite_dir
        self.solution_path = solution_path
        self.time_limit = time_limit
        self.input_extension = input_extension
        self.output_extension = output_extension
        self.actualout_dir = actualout_dir
        self.language = solution_path[solution_path.rfind('.') + 1:]
        # Compile
        if self.language in ('c', 'cpp'):
            if system('g++ ./' + solution_path + ' -o ./judgingprocess'):
                raise CompileError(f'Failed to compile "{solution_path}".')

        if actualout_dir is not None and not exists(actualout_dir):
            makedirs(actualout_dir)

        self.testcnt = 0
        self.testsuite = SynAssets(list[TestCaseInfo]())
        for filename in listdir(intestsuite_dir):
            if not filename.endswith('.' + input_extension):
                continue
            testname = filename[:filename.rfind('.')]
            if not exists(outtestsuite_dir + '/' + testname + '.' + output_extension):
                raise MissingFileException(
                    'Mising output file for test case "%s" (Thiếu file output).' % testname)
            self.testsuite.assets.append(
                TestCaseInfo(
                    order=self.testcnt,
                    testname=testname,
                    input_file_path=intestsuite_dir + '/' + filename,
                    output_file_path=outtestsuite_dir + '/' + testname + '.' + output_extension
                )
            )
            self.testcnt += 1

    def start(self) -> None:
        if self.accnt == 0:
            result = _format.formating(
                f'Failed ({self.accnt}/{self.testcnt}).', _format.BOLD, _format.RED)
        elif self.accnt == self.testcnt:
            result = _format.formating(
                f'Accepted ({self.accnt}/{self.testcnt}).', _format.BOLD, _format.GREEN)
        else:
            result = _format.formating(
                f'Partial ({self.accnt}/{self.testcnt}).', _format.BOLD, _format.YELLOW)

        print(_format.formating(f'  > Result: ',
              _format.BOLD, _format.CYAN) + result)

        if self.language in ('c', 'cpp'):
            if osname() == 'Linux':
                systemrun('killall -KILL judgingprocess',
                          stdout=DEVNULL, stderr=DEVNULL)
                remove('judgingprocess')
            elif osname() == 'Darwin':
                systemrun('sudo killall -9 \'judgingprocess\'',
                          stdout=DEVNULL, stderr=DEVNULL)
                remove('judgingprocess')
            elif osname() == 'Windows':
                systemrun('taskkill /F /IM judgingprocess.exe',
                          stdout=DEVNULL, stderr=DEVNULL)
                remove('judgingprocess.exe')


class SingleJudge(_BaseJudge):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __run_testcase(
        self,
        testcase_info: TestCaseInfo,
        actual_output_file_path=None
    ):
        if self.language == 'py':
            pyrun = 'py' if osname() == 'Windows' else 'python3'
            command = f'{pyrun} {self.solution_path} < {testcase_info.input_file_path}'
        elif self.language in ('c', 'cpp'):
            command = f'./judgingprocess < {testcase_info.input_file_path}'
        if osname() == 'Windows':
            command = f'cmd /c "{command}'
        self.judge_result = JudgeResult(testcase_info)

        run_thread = StoppableThread(target=self.__visual_run, args=(command,))
        run_thread.start()
        run_thread.join(self.time_limit)
        if run_thread.exception is not None:
            raise run_thread.exception
        if run_thread.is_alive():
            run_thread.kill()
            raise TimeLimitExceeded()
        if (
            self.language == 'py' and self.judge_result.output.startswith(
                'Traceback')
            or
            self.language in ('c', 'cpp') and 'terminate called after throwing' in self.judge_result.output
        ):
            raise InvalidReturn()

        if actual_output_file_path is not None:
            with open(actual_output_file_path, 'w', encoding='utf-8') as actual_outputfile:
                actual_outputfile.write(self.judge_result.output)
        with open(testcase_info.output_file_path, 'r', encoding='utf-8') as expected_outputfile:
            if self.judge_result.output.strip() == expected_outputfile.read().strip():
                self.judge_result.result = 'AC'
            else:
                self.judge_result.result = 'WA'

    def __visual_run(self, command):
        start_time = time()
        process = systemrun(command, stdout=PIPE)
        end_time = time()
        self.judge_result.cost_time = end_time - start_time
        if process.returncode != 0:
            raise RunTimeError()
        with TextIOWrapper(BytesIO(process.stdout)) as outstream:
            output = outstream.read()
            self.judge_result.output = output

    def start(self) -> None:
        print('\nStart judgment:')
        self.accnt = 0
        for i, testcase_info in enumerate(self.testsuite.assets):
            actual_output_file_path = None
            if self.actualout_dir is not None:
                actual_output_file_path = self.actualout_dir + \
                    '/' + testcase_info.testname + '.txt'
            try:
                self.__run_testcase(testcase_info, actual_output_file_path)
                if self.judge_result.result == 'WA':
                    status = _format.formating(
                        'Wrong answer (WA).', _format.RED)
                elif self.judge_result.result == 'AC':
                    status = _format.formating(
                        'Accepted (AC) in %.3fs.' % self.judge_result.cost_time, _format.GREEN)
                    self.accnt += 1
            except InvalidReturn:
                status = _format.formating('Invalid Return (IR).', _format.RED)
            except RunTimeError:
                status = _format.formating(
                    'Run Time Error (RTE).', _format.RED)
            except TimeLimitExceeded:
                status = _format.formating(
                    'Time Limit Exceeded (TLE).', _format.RED)
            print(
                f'- Testcase {i}."{_format.formating(testcase_info.testname, _format.CYAN)}": {status}')
        super().start()


class MultiJudge(_BaseJudge):
    def __init__(self, *args, number_of_judges=_DEFAULT.NUMBER_OF_JUDGES, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.number_of_judges = number_of_judges

    def start(self) -> None:
        print('\nStart judgment:')
        self.accnt = 0

        for i in range(len(self.testsuite.assets)):
            string = f'- Testcase {i}."{_format.formating(self.testsuite.assets[i].testname, _format.CYAN)}": Waiting...'
            self.testsuite.assets[i].display_start_index = string.find(
                'Waiting...') - len(_format.CYAN) - len(_format.END)
            print(string)

        self.stdcursor = SynAssets(Cursor(self.testcnt))
        self.stdcursor.lock.acquire()
        self.stdcursor.lock.release()
        self.testsuite.assets = self.testsuite.assets[::-1]

        judges = [TestCaseManager(self, self.time_limit, self.solution_path, self.actualout_dir,
                                  self.testsuite) for _ in range(self.number_of_judges)]

        for judge in judges:
            judge.start()

        for judge in judges:
            judge.join()

        self.stdcursor.lock.acquire()
        self.stdcursor.assets.jumpto(self.testcnt, 0)
        self.stdcursor.lock.release()

        super().start()
