class AbstractComputeEnv:
    def init(self) -> dict:
        pass

    def upload(self, filename: str, target_filename: str = None) -> None:
        pass

    def download(self, input_filename: str, output_filename: str) -> None:
        pass

    def delete(self, filename: str) -> None:
        pass

    def list_files(self, path: str = None) -> list[str]:
        pass

    def destroy(self) -> None:
        pass
