from .compute_env.AbstractComputeEnv import AbstractComputeEnv
from .compute_env.LambdaComputeEnv import LambdaComputeEnv
from .compute_env.BatchComputeEnv import BatchComputeEnv


class Efs:
    __compute_env: AbstractComputeEnv = None
    __DEFAULT_COMPUTE_ENV = 'lambda'

    def __init__(self, file_system_id: str, options: dict = None, logger: object = None,
                 compute_env_name: str = None) -> None:
        compute_env_name = compute_env_name if compute_env_name is not None else self.__DEFAULT_COMPUTE_ENV
        if compute_env_name == 'lambda':
            self.__compute_env = LambdaComputeEnv(file_system_id, options, logger)
        elif compute_env_name == 'batch':
            self.__compute_env = BatchComputeEnv(file_system_id, options if options is not None else {}, logger)
        else:
            raise Exception('Wrong compute environment')

    def init(self) -> dict:
        return self.__compute_env.init()

    def upload(self, filename: str, target_filename: str = None) -> None:
        self.__compute_env.upload(filename, target_filename)

    def download(self, input_filename: str, output_filename: str) -> None:
        self.__compute_env.download(input_filename, output_filename)

    def delete(self, filename: str) -> None:
        self.__compute_env.delete(filename)

    def delete_async(self, filename: str) -> str:
        return self.__compute_env.delete_async(filename)

    def list_files(self, path: str = None) -> list[str]:
        return self.__compute_env.list_files(path)

    def destroy(self) -> None:
        self.__compute_env.destroy()
