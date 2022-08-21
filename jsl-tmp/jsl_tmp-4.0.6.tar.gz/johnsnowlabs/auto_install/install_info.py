from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Union, Callable, Any
from johnsnowlabs import settings
from johnsnowlabs.abstract_base.pydantic_model import WritableBaseModel
from johnsnowlabs.utils.jsl_secrets import JslSecrets
from johnsnowlabs.utils.enums import ProductName, JvmHardwareTarget, PyInstallTypes
from johnsnowlabs.utils.lib_version import LibVersion

from pydantic import BaseConfig, BaseModel


class InstallFileInfoBase(WritableBaseModel):
    file_name: str
    product: ProductName
    compatible_spark_version: Union[str, LibVersion]
    product_version: Union[str, LibVersion]

    # install_type: Optional[JvmHardwareTarget]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compatible_spark_version = LibVersion(self.compatible_spark_version)
        self.product_version = LibVersion(self.product_version)


class PyInstallInfo(InstallFileInfoBase):
    install_type: PyInstallTypes


class JvmInstallInfo(InstallFileInfoBase):
    install_type: JvmHardwareTarget


class InstallSuite(WritableBaseModel):
    ocr: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    nlp: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    hc: Optional[Tuple[JvmInstallInfo, PyInstallInfo]] = None
    secrets: Optional[JslSecrets] = None


class LocalPy4JLib(WritableBaseModel):
    java_lib: Optional[JvmInstallInfo] = None
    py_lib: Optional[PyInstallInfo] = None

    def get_java_path(self):
        return f'{settings.java_dir}/{self.java_lib.file_name}'

    def get_py_path(self):
        return f'{settings.py_dir}/{self.py_lib.file_name}'


class RootInfo(WritableBaseModel):
    version: Union[str, LibVersion]
    run_from: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = LibVersion(self.version)


class InstallSuite(WritableBaseModel):
    info: RootInfo
    nlp: LocalPy4JLib
    ocr: Optional[LocalPy4JLib] = None
    hc: Optional[LocalPy4JLib] = None
    secrets: Optional[JslSecrets] = None
    optional_pure_py_jsl: Optional[LocalPy4JLib] = None
    optional_pure_py_jsl_dependencies: Optional[LocalPy4JLib] = None


class InstallFileInfovBase2(WritableBaseModel):
    file_name: str
    product: ProductName
    compatible_spark_version: Union[str, LibVersion]
    product_version: Union[str, LibVersion]

    # install_type: Optional[JvmHardwareTarget]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compatible_spark_version = LibVersion(self.compatible_spark_version)
        self.product_version = LibVersion(self.product_version)


class InstallFolder(WritableBaseModel):
    infos: Dict[str, Union[PyInstallInfo, JvmInstallInfo]]

    def get_product_entry(self, product: ProductName):
        try:
            return self.infos[next(filter(lambda x: product.value in x, self.infos.keys()))]
        except StopIteration:
            return None
