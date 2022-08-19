import io
import os
from abc import ABC, abstractmethod
from contextlib import contextmanager

from .file_sections import csv_section


class FreelanceExportData(ABC):

    def __init__(self, file_data: tuple[str] = tuple()) -> None:
        self._data = file_data

    @abstractmethod
    def complete_file(self) -> tuple[tuple]:
        pass

    @abstractmethod
    def extract_sections(self, section: str) -> tuple[tuple]:
        pass


class FreelancePlcData(FreelanceExportData):
    pass


class FreelancePleData(FreelanceExportData):
    pass


class FreelanceCsvData(FreelanceExportData):

    def complete_file(self) -> tuple[tuple]:
        return tuple(tuple(row.split(";")) for row in self._data)

    def extract_sections(self, section: str) -> tuple[tuple]:
        begin_key, end_key = csv_section(section)
        search_dict = {}
        search_count = 0
        for line in range(len(self._data)):
            if begin_key in self._data[line]:
                search_dict[search_count] = [line]
            if end_key in self._data[line]:
                search_dict[search_count].append(line)
                search_count += 1
        section_list = [self._data[value[0]:value[1]] for value in search_dict.values()]
        return tuple(section_list)


class FreelanceReader:
    """
    Freelane API Context Manager 
    """

    def __init__(self, file_name: str) -> None:
        filename, self.file_extension = os.path.splitext(file_name)
        if self.file_extension.lower() != ".csv":
            raise AttributeError(f'{self.file_extension} is not supported with this Context Manager!')
        self._wrapper = open(file_name, "r", newline="", encoding='utf-16')

    def __enter__(self) -> FreelanceExportData:
        if self.file_extension.lower() == ".csv":
            return FreelanceCsvData(tuple(row.strip() for row in self._wrapper))
        raise AttributeError(f'{self.file_extension} is currently not supported')

    def __exit__(self, error: Exception, value: object, traceback: object) -> None:
        self._wrapper.close()
