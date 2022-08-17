import glob
from pandas import DataFrame
from src.domain.Server.Server import Server
from urllib.parse import unquote


class ReadAllLogsFileIntoMemoryUsingPandas:
    def __init__(self, pd):
        self.pd = pd

    def process(self, server: Server) -> DataFrame:
        data: DataFrame = DataFrame()
        data_frames: list = []
        for log_file in self.get_files_list(f"{server.source_path}{server.includes}"):
            df = self.pd.read_csv(
                log_file,
                sep=r'\s(?=(?:[^"]*"[^"]*")*[^"]*$)(?![^\[]*\])',
                engine="python",
                usecols=[0, 3, 4, 5, 6, 7, 8],
                names=["ip", "str_datetime", "request", "status", "size", "referer", "user_agent"],
                na_values="-",
                header=None,
                encoding="utf-8-sig",
                converters={"request": unquote},
            )
            data_frames.append(df)

            data = self.pd.concat(data_frames, axis=0, ignore_index=True)
        return data

    def get_files_list(self, files_pattern: object) -> list[str]:
        files: list = glob.glob(files_pattern)
        files.sort()
        return files
