from typing import Optional, List
from collections import UserList

import pydantic

from .error import (
    LicenseNotFoundError,
    LicenseOriginURLMissingError,
    MultipleLicensesWarning,
)


class License(pydantic.BaseModel):
    direct_url: Optional[str]  # radio optional <a> (and url type)
    xml_url: Optional[str]  # radio optional <a> (and url type)
    full_name: str
    spdx_id: str
    approved_osi: bool
    approved_fsf: bool
    license_header_text: Optional[str]  # format region
    license_text: str
    obsolete: bool

    @pydantic.root_validator(pre=True)
    @classmethod
    def check_direct_or_xml_url_available(cls, values):
        if not ("direct_url" in values or "xml_url" in values):
            raise LicenseOriginURLMissingError(values)
        return values


class Licenses(UserList):
    # convert to list and from list init and more
    def __init__(self, licenses: List[License]):
        self.data = licenses

    def get(self, name):
        pass

    def filter(self, prop):
        pass

    def __getitem__(self, name):  # only one and exact
        # change filter to get
        # check all name and see you got one or more as test
        """When using getitem to get the license, you have to enter exact
        spdx_id or full_name. #filter

        Args:
            name (_type_): _description_

        Returns:
            _type_: _description_
        """
        result = list(
            filter(
                lambda license: (license.full_name == name)
                or (license.spdx_id == name),
                self.data,
            )
        )
        if len(result) == 0:
            raise LicenseNotFoundError(name)
        elif len(result) == 1:
            return result[0]
        else:
            MultipleLicensesWarning(name)
            return result

    # def __getattr__(self, name): # more than one? with search
    #     return get()
