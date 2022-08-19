import distutils.util
import os

from pytestapilib.core.file import FileManager
from pytestapilib.core.log import log
from pytestapilib.core.system import ProjectVariables


class MainConfig:
    YAML = FileManager(ProjectVariables.MAIN_CONFIG_YML_PATH).read_yml()


class WireMockConfig:
    log.info('Initializing wiremock configuration')

    __WIREMOCK = MainConfig.YAML['wiremock']

    is_sys_var_available = 'PY_TEST_API_WIREMOCK_ENABLED' in os.environ
    log.info(f'Does PY_TEST_API_WIREMOCK_ENABLED sys var exist? {is_sys_var_available}')

    ENABLED = bool(distutils.util.strtobool(os.environ['PY_TEST_API_WIREMOCK_ENABLED'])) \
        if is_sys_var_available else __WIREMOCK['enabled']
    HOST = __WIREMOCK['host']
    PORT = __WIREMOCK['port']
    DIR = __WIREMOCK['dir']
    JAR = __WIREMOCK['jar']
    log.info(f'WireMock config: ENABLED = {ENABLED}, PORT = {PORT}, DIR = {DIR}, JAR = {JAR}')
