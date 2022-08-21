import shutil
import urllib.request
from typing import Union, List, Optional
from urllib.request import urlopen

import requests

from johnsnowlabs.utils.enums import JvmHardwareTarget, PyInstallTypes, ProductName
from johnsnowlabs.abstract_base.pydantic_model import WritableBaseModel
from johnsnowlabs.utils.enums import SparkVersion
from johnsnowlabs.utils.lib_version import LibVersion


class MyJslLicenseDataResponse(WritableBaseModel):
    """Representation of a URL"""
    id: str
    license_type: str
    end_date: str
    plattform: Optional[str]
    products: List[ProductName]
    product_name: ProductName
