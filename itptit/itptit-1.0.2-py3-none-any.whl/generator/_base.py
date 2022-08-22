from abc import abstractmethod, ABC
from os.path import exists
from os import makedirs
from time import time
from typing import Any, Dict, List
from ..common.exceptions import FailedToCreateTestCaseException
from ..common import (
    cursor as _cursor,
    format as _format,
    stdout as _stdout
)


class DEFAULT:
    class TESTCASEFAMILY:
        NUMBER_OF_TESTS = 1
        ARGS_LIST = []
        KWARGS_LIST = []
        NAME = 'AnonymousTest'

    class GENERATOR:
        SKIP_ERRORS = False
        FILE_SIZE_LIMIT = None

        class INPUT:
            WRITE_MODE = 0
            FILE_EXTENSION = 'in'
            INDEXING = True

        class OUTPUT:
            WRITE_MODE = 2
            INPUT_FILE_EXTENSION = 'in'
            FILE_EXTENSION = 'out'


class TestCaseFamily:
    '''
    Family of test cases that share the same generator function.

    Họ test case sử dụng chung hàm sinh input.
    '''

    def __init__(
            self,
            gen_func,
            number_of_test_cases: int = DEFAULT.TESTCASEFAMILY.NUMBER_OF_TESTS,
            args_list: List[List[Any]] = DEFAULT.TESTCASEFAMILY.ARGS_LIST,
            kwargs_list: List[Dict[Any, Any]
                              ] = DEFAULT.TESTCASEFAMILY.KWARGS_LIST,
            name: str = DEFAULT.TESTCASEFAMILY.NAME):
        '''
        ### TestCaseFamily constructor.

        ## Parameters

        - gen_func: function

            Generate function which is the function use to generate test cases.

            Hàm sinh nội dung cho input của test case.

        - number_of_test_cases: int (Default: `1`)

            The number of test cases that need to be created using this TestCaseFamily.

            Số lượng test case sẽ sinh ra từ họ này.

        - args_list: List[List[Any]] (Default: `[]`)

            A list contains the position arguments for each test case.

            List chứa các list con. Mỗi list con chứa các đối số theo vị trí sử dụng cho hàm sinh trong mỗi test case.

        - kwargs_list: List[Dict[Any, Any]] (Default: `[]`)

            A list contains the keyword arguments for each test case.

            List chứa các list con. Mỗi list con chứa các đối số theo từ khóa sử dụng cho hàm sinh trong mỗi test case.

        - name: str (Default: `'AnonymousTest'`)

            Name for the TestCaseFamily.

            Tên cho họ test case.
        '''
        self.__gen_func = gen_func
        self.__number_of_test_cases = number_of_test_cases
        if len(args_list) != number_of_test_cases:
            args_list += [[]
                          for _ in range(number_of_test_cases - len(args_list))]
        if len(kwargs_list) != number_of_test_cases:
            kwargs_list += [{}
                            for _ in range(number_of_test_cases - len(kwargs_list))]
        self.__args_list = args_list
        self.__kwargs_list = kwargs_list
        self.__name = name

    @property
    def gen_func(self): return self.__gen_func
    @property
    def number_of_test_cases(self) -> int: return self.__number_of_test_cases
    @property
    def args_list(self) -> List[List]: return self.__args_list
    @property
    def kwargs_list(self) -> List[Dict]: return self.__kwargs_list
    @property
    def name(self) -> str: return self.__name

    @number_of_test_cases.setter
    def number_of_test_cases(self, value: int) -> None:
        self.__number_of_test_cases = value

    @args_list.setter
    def args_list(self, value: List[List]) -> None:
        self.__args_list = value

    @kwargs_list.setter
    def kwargs_list(self, value: List[Dict]) -> None:
        self.__kwargs_list = value

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    def create(self, gen_func_args: List[Any] = [], gen_func_kwargs: Dict[Any, Any] = {}) -> str:
        '''
        ### Create input for a test case.

        ## Parameters

        - gen_func_args: List[Any] (Default: `[]`)

            Position arguments for generate function.

            Đối số theo vị trí cho hàm sinh.

        - gen_func_kwargs: Dict[Any, Any] (Default: `{}`)

            Keyword arguments for generate function.

            Đối số theo từ khóa cho hàm sinh.

        ## Returns

        A string which is content of a test case created from generate function of itself.

        Nội dung input cho một test case sinh ra từ họ test case này.
        '''
        return _stdout.get(self.__gen_func, *gen_func_args, **gen_func_kwargs)


class _BaseGenerator(ABC):
    _static_write_mode: int = ...
    _default_write_mode: int = ...

    def __init__(
        self,
        target_dir: str,
        file_extension: str,
        skip_errors: bool,
        file_size_limit: int
    ):
        self.__target_dir = self._get_dir(target_dir)
        self.__file_extension = file_extension
        self.__write_mode = self._default_write_mode
        self.__skip_errors = skip_errors
        self.__file_size_limit = file_size_limit

    @property
    def target_dir(self) -> str: return self.__target_dir
    @property
    def file_extension(self) -> str: return self.__file_extension
    @property
    def write_mode(self) -> int: return self.__write_mode
    @property
    def skip_errors(self) -> bool: return self.__skip_errors
    @property
    def file_size_limit(self) -> int: return self.__file_size_limit
    @target_dir.setter
    def target_dir(self, value: str) -> None:  self.__target_dir = value
    @file_extension.setter
    def file_extension(self, value: str) -> None: self.file_extension = value
    @write_mode.setter
    def write_mode(self, value: int) -> None: self.__write_mode = value
    @skip_errors.setter
    def skip_errors(self, value: bool) -> None: self.skip_errors = value
    @file_size_limit.setter
    def file_size_limit(self, value: int) -> None: self.file_size_limit = value

    @classmethod
    def _get_dir(cls, dir: str) -> str:
        while dir[-1] == '/':
            dir = dir[:-1]
        if not exists(dir):
            makedirs(dir)
        return dir

    @classmethod
    def _overwrite_ask(cls, filename: str, write_mode) -> int:
        if write_mode == 2:
            return 2
        print('-' * 50)
        print(_format.formating(
            f'"{filename}" already exists!', _format.YELLOW))
        print(_format.formating('1: ', _format.GREEN) + "Overwrite.")
        print(_format.formating('2: ', _format.GREEN) + "Overwrite for all.")
        print(_format.formating('Default: ', _format.CYAN) + "Skip.")
        choice = input("You want to: ")
        _cursor.clear_lines(6)
        if choice in ('1', '2'):
            return int(choice)
        return 0

    @classmethod
    def _create_file(
        cls,
        repository: List[str],
        path: str,
        filename: str,
        is_static_gen: bool,
        skip_error: bool,
        file_size_limit: int,
        *args,
        **kwargs
    ) -> str:
        status_choices = ('Skip', 'Overwrite', 'Overwrite')
        status_color = {
            'New': _format.GREEN,
            'Skip': _format.GRAY,
            'Overwrite': _format.CYAN,
            'Fail': _format.RED
        }
        status = 'New'
        if exists(path + '/' + filename):
            if filename not in repository:
                if is_static_gen:
                    cls._static_write_mode = cls._overwrite_ask(
                        filename, cls._static_write_mode)
                    status = status_choices[cls._static_write_mode]
                else:
                    cls.write_mode = cls._overwrite_ask(
                        filename, cls.write_mode)
                    status = status_choices[cls.write_mode]
        repository.append(filename)
        if status == 'Skip':
            return '- ' + _format.formating(f'Skip: "{filename}".', status_color['Skip'])
        with open(path + '/' + filename, 'w', encoding='utf-8') as f:
            print(_format.formating('Creating...', _format.YELLOW))
            start_time = time()
            content = cls._create_test_case(*args, **kwargs)
            end_time = time()
            _cursor.clear_lines(1)
            try:
                if content.strip() == '':
                    raise FailedToCreateTestCaseException(
                        filename, 'This file has no content (File trống).')
                file_size = len(content) + content.count('\n')
                if file_size_limit and file_size >= file_size_limit:
                    raise FailedToCreateTestCaseException(
                        filename, f'This file exceeded the set capacity limit (Expected: {file_size_limit}b, actual: {file_size}b) (Vượt quá giới hạn dung lượng đã thiết lập).')
            except FailedToCreateTestCaseException as e:
                if skip_error:
                    return '- ' + _format.formating(f'Fail: {e.msg}', status_color['Fail'])
                raise e
            f.write(content)
            return '- ' + _format.formating(status, status_color[status]) + ': Created file "%s" successfully in %.5fs!' % (filename, end_time - start_time)

    @classmethod
    def _generate_init(cls, is_static_gen: bool):
        if is_static_gen:
            cls._static_write_mode = cls._default_write_mode
        else:
            cls.write_mode = cls._default_write_mode

    @classmethod
    @abstractmethod
    def _generate(cls, *args, **kwargs): ...
    @classmethod
    @abstractmethod
    def _create_test_case(cls, *args, **kwargs): ...
    @classmethod
    @abstractmethod
    def generate(cls, *args, **kwargs): ...

    @abstractmethod
    def start(self, *args, **kwargs): ...
