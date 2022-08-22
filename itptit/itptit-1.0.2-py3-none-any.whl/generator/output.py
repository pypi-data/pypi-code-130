from typing import Optional
from ..common.exceptions import (
    CompileError,
    WrongFileExtensionException
)
from ._base import (
    _BaseGenerator,
    DEFAULT
)
from os import (
    listdir,
    popen,
    remove,
    system
)
from platform import system as osname
from ..common import format


class Generator(_BaseGenerator):
    '''
    ### Test case's output generator.
    '''

    _static_write_mode: int = DEFAULT.GENERATOR.OUTPUT.WRITE_MODE
    _default_write_mode: int = DEFAULT.GENERATOR.OUTPUT.WRITE_MODE

    def __init__(
        self,
        input_testsuite_dir: str,
        solution_path: str,
        target_dir: str,
        *,
        input_file_extension: str = DEFAULT.GENERATOR.OUTPUT.INPUT_FILE_EXTENSION,
        file_extension: str = DEFAULT.GENERATOR.OUTPUT.FILE_EXTENSION,
        skip_errors: bool = DEFAULT.GENERATOR.SKIP_ERRORS,
        file_size_limit: Optional[int] = DEFAULT.GENERATOR.FILE_SIZE_LIMIT
    ):
        super().__init__(target_dir, file_extension, skip_errors, file_size_limit)
        self.__solution_path = solution_path
        self.__input_testsuite_dir = input_testsuite_dir
        self.__input_file_extension = input_file_extension

    @property
    def input_testsuite_dir(self) -> str: return self.__input_testsuite_dir
    @property
    def solution_path(self) -> str: return self.__solution_path
    @property
    def input_file_extension(self) -> str: return self.__input_file_extension

    @input_testsuite_dir.setter
    def input_testsuite_dir(
        self, value) -> None: self.__input_testsuite_dir = value

    @solution_path.setter
    def solution_path(self, value) -> None: self.__solution_path = value

    @input_file_extension.setter
    def input_file_extension(
        self, value) -> None: self.input_file_extension = value

    @classmethod
    def _create_test_case(
        cls,
        input_path: str,
        solution_path: str,
        language: str
    ) -> str:
        if language == 'py':
            pyrun = 'py' if osname() == 'Windows' else 'python3'
            command = f'{pyrun} {solution_path} < {input_path}'
        elif language in ('c', 'cpp'):
            command = 'solution < ' + input_path
        if osname() == 'Windows':
            command = f'cmd /c "{command}'
        with popen(command) as output:
            return output.read()

    @classmethod
    def _generate(
        cls,
        source_dir: str,
        solution_path: str,
        target_dir: str,
        input_file_extension: str,
        file_extension: str,
        is_static_gen: bool,
        skip_errors: bool,
        file_size_limit: int
    ) -> bool:
        cls._generate_init(is_static_gen)
        source_dir = cls._get_dir(source_dir)
        target_dir = cls._get_dir(target_dir)
        repository = []
        failed = False
        wrong_file_extension = True
        language = solution_path[solution_path.rfind('.') + 1:]
        if language in ('c', 'cpp'):
            if system('g++ ./' + solution_path + ' -o ./solution'):
                raise CompileError(f'Failed to compile "{solution_path}".')
        warm_up = False
        for file in listdir(source_dir):
            if not file.endswith('.' + input_file_extension):
                continue
            if not warm_up:
                # Prepare step to warm up the generator - does not cause errors in time when creating tests.
                for i in range(2):
                    cls._create_test_case(
                        source_dir + '/' + file,
                        solution_path,
                        language
                    )
                warm_up = True
            wrong_file_extension = False
            test_case_name = file[:file.rfind('.')]
            res = cls._create_file(
                repository,
                target_dir,
                test_case_name + '.' + file_extension,
                is_static_gen,
                skip_errors,
                file_size_limit,
                source_dir + '/' + file,
                solution_path,
                language
            )
            if 'Fail' in res:
                failed = True
            print(res)
        if language in ('c', 'cpp'):
            if osname() == 'Linux':
                remove('./solution')
            elif osname() == 'Darwin':
                remove('./solution')
            elif osname() == 'Windows':
                remove('./solution.exe')
        if wrong_file_extension:
            raise WrongFileExtensionException(input_file_extension)
        if failed:
            print(format.formating(
                "All test case's outputs have been generated, except for a few.", format.YELLOW))
            return False
        print(format.formating(
            "All test case's outputs have been generated.", format.GREEN))
        return True

    @classmethod
    def generate(
        cls,
        input_testsuite_dir: str,
        solution_path: str,
        target_dir: str,
        *,
        input_file_extension: str = DEFAULT.GENERATOR.OUTPUT.INPUT_FILE_EXTENSION,
        file_extension: str = DEFAULT.GENERATOR.OUTPUT.FILE_EXTENSION,
        skip_errors: bool = DEFAULT.GENERATOR.SKIP_ERRORS,
        file_size_limit: Optional[int] = DEFAULT.GENERATOR.FILE_SIZE_LIMIT
    ) -> bool:
        print('\nStart generating output for test cases:')
        return cls._generate(
            input_testsuite_dir,
            solution_path,
            target_dir,
            input_file_extension,
            file_extension,
            True,
            skip_errors,
            file_size_limit
        )

    def start(self) -> bool:
        print('\nStart generating output for test cases:')
        return self._generate(
            self.__input_testsuite_dir,
            self.__solution_path,
            self.target_dir,
            self.__input_file_extension,
            self.file_extension,
            False,
            self.skip_errors,
            self.file_size_limit
        )
