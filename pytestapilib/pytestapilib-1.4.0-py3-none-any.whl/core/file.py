import json
import sys
from typing import Any

import yaml

from pytestapilib.core.log import log
from pytestapilib.core.system import ProjectVariables


class FileManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        if sys.platform.startswith('win32'):
            self.file_path = file_path.replace('/', '\\')

    def read_yml(self) -> Any:
        file_path = ProjectVariables.PROJECT_ROOT_DIR + self.file_path
        log.info(f'Reading {file_path}')
        with open(file_path, encoding='UTF-8') as stream:
            return yaml.safe_load(stream)

    def write(self, content):
        try:
            with open(self.file_path, 'w', encoding="utf8") as file:
                file.write(content)
            log.debug('File has been created/rewritten: %s', self.file_path)
        except IOError:
            log.error('File has not been found: %s', self.file_path)

    def dump(self, content):
        try:
            with open(self.file_path, 'w', encoding="utf8") as file:
                json.dump(content, file)
            log.debug('File has been created/rewritten: %s', self.file_path)
        except IOError:
            log.error('File has not been found: %s', self.file_path)
