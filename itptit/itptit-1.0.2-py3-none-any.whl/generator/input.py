from typing import (
    Any,
    Dict,
    List,
    NoReturn,
    Optional
)
from ._base import (
    DEFAULT,
    TestCaseFamily,
    _BaseGenerator
)
from ..common import format


class Generator(_BaseGenerator):

    _static_write_mode: int = DEFAULT.GENERATOR.INPUT.WRITE_MODE
    _default_write_mode: int = DEFAULT.GENERATOR.INPUT.WRITE_MODE

    def __init__(
        self,
        target_dir: str,
        *test_case_families: TestCaseFamily,
        file_extension: str = DEFAULT.GENERATOR.INPUT.FILE_EXTENSION,
        indexing: bool = DEFAULT.GENERATOR.INPUT.INDEXING,
        skip_errors: bool = DEFAULT.GENERATOR.SKIP_ERRORS,
        file_size_limit: Optional[int] = DEFAULT.GENERATOR.FILE_SIZE_LIMIT
    ):
        super().__init__(target_dir, file_extension, skip_errors, file_size_limit)
        self.__family_pool: List[TestCaseFamily] = [*test_case_families]
        self.__indexing = indexing

    @property
    def family_pool(self): return self.__family_pool
    @property
    def indexing(self): return self.__indexing

    @family_pool.setter
    def family_pool(
        self, value: List[TestCaseFamily]): self.__family_pool = value

    @indexing.setter
    def indexing(self, value: bool): self.__indexing = value

    def add(self, *args: TestCaseFamily | Any) -> NoReturn:
        for obj in args:
            family = obj
            if not isinstance(obj, TestCaseFamily):
                family = TestCaseFamily(obj)
            self.__family_pool.append(family)

    def remove(self, arg: TestCaseFamily | Any) -> NoReturn:
        if isinstance(arg, TestCaseFamily):
            self.__family_pool.remove(arg)
        else:
            for family in self.__family_pool:
                if arg == family.gen_func:
                    self.__family_pool.remove(family)

    @classmethod
    def _create_test_case(
        cls,
        family: TestCaseFamily,
        gen_func_args: List[Any],
        gen_func_kwargs: Dict[Any, Any]
    ) -> str:
        return family.create(gen_func_args, gen_func_kwargs)

    @classmethod
    def _generate(
        cls,
        target_dir: str,
        file_extension: str,
        indexing: bool,
        is_static_gen: bool,
        skip_errors: bool,
        file_size_limit: int,
        *families: TestCaseFamily
    ) -> bool:
        cls._generate_init(is_static_gen)
        target_dir = cls._get_dir(target_dir)
        repository = []
        failed = False
        for family in families:
            for itest in range(family.number_of_test_cases):
                if indexing:
                    test_case_name = str(len(repository))
                else:
                    i_tmp = itest
                    while True:
                        name_tmp = f'{family.name}_{i_tmp}'
                        if name_tmp not in repository:
                            test_case_name = name_tmp
                            break
                        i_tmp += 1
                res = cls._create_file(
                    repository,
                    target_dir,
                    test_case_name + '.' + file_extension,
                    is_static_gen,
                    skip_errors,
                    file_size_limit,
                    family,
                    family.args_list[itest],
                    family.kwargs_list[itest]
                )
                if 'Fail' in res:
                    failed = True
                print(res)
        if failed:
            print(format.formating(
                "All test case's inputs have been generated, except for a few.", format.YELLOW))
            return False
        print(format.formating(
            "All test case's inputs have been generated.", format.GREEN))
        return True

    @classmethod
    def generate(
        cls,
        target_dir: str,
        *families: TestCaseFamily,
        file_extension: str = DEFAULT.GENERATOR.INPUT.FILE_EXTENSION,
        indexing: bool = DEFAULT.GENERATOR.INPUT.INDEXING,
        skip_errors: bool = DEFAULT.GENERATOR.SKIP_ERRORS,
        file_size_limit: Optional[int] = DEFAULT.GENERATOR.FILE_SIZE_LIMIT
    ) -> bool:
        print('\nStart generating input for test cases:')
        return cls._generate(
            target_dir,
            file_extension,
            indexing,
            True,
            skip_errors,
            file_size_limit,
            *families
        )

    def start(self) -> bool:
        print('\nStart generating input for test cases:')
        return self._generate(
            self.target_dir,
            self.file_extension,
            self.__indexing,
            False,
            self.skip_errors,
            self.file_size_limit,
            *self.__family_pool
        )
