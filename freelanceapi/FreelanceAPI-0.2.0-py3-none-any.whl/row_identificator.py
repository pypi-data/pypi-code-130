from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel

from .sections.area_dict import AreaDict
from .sections.eam_dict import EamRecordDict
from .sections.gwy_dict import GwyDict
from .sections.hd_dict import MsrRefDict, ParaRefDict
from .sections.hw2_dict import BeginIODescriptionDict, Hw2BlobDict, Hw2NodeDict
from .sections.msr_dict import MsrRecordDict, UidAccDict
from .sections.node_dict import PbNodeDict
from .sections.para_dict import ParaDataDict
from .sections.pbaum_dict import PbvObjpathDict
from .sections.resourcen_dict import EamResourceDict
from .utils import (
    Create, create_ascii_hex, create_string_from_dict_with_list_of_dicts, create_string_from_dict_with_string
    )


class RowIdentification(BaseModel, ABC):
    ID: str = None

    def _get_string_from_dict_with_string(self, dict_of_strings: Dict) -> str:
        created_string = Create(dict_of_strings)
        return created_string.execute(create_string_from_dict_with_string(sep=";"))

    def _get_string_from_dict_with_dict(self, dict_with_list_of_dicts: Dict) -> str:
        created_string = Create(dict_with_list_of_dicts)
        return created_string.execute(create_string_from_dict_with_list_of_dicts(sep=";"))

    def _get_string_ascii_hex(self, ascii_list: List[str]) -> str:
        created_string = Create(ascii_list)
        return created_string.execute(create_ascii_hex())

    @abstractmethod
    def string(self) -> str:
        pass


# sourcery skip: remove-duplicate-dict-key
class MsrRec(RowIdentification):
    NA: int = None
    MP: str = None
    LB: str = None
    MT: str = None
    ST: str = None
    LT: str = None
    NI1: str = None
    AD: int = None
    SB: int = None
    NI2: str = None
    NI3: str = None
    NI4: str = None
    NI5: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class UidAcc(RowIdentification):
    LEN: int = None
    PARA: list = None

    def string(self) -> str:
        uid_string = self._get_string_from_dict_with_dict(self.PARA)
        normal_string = self._get_string_from_dict_with_string(self.dict(exclude={"PARA"}))
        return f"{normal_string};{uid_string}"


class ParaData(RowIdentification):
    LEN: int = None
    PARA: list = None

    def string(self) -> str:
        para_string = self._get_string_from_dict_with_dict(self.PARA)
        normal_string = self._get_string_from_dict_with_string(self.dict(exclude={"PARA"}))
        return f"{normal_string};{para_string}"


class PBNode(RowIdentification):
    NA: int = None
    MT: str = None
    FN: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class EamRecord(RowIdentification):
    NA: int = None
    VN: str = None
    NI1: int = None
    DT: str = None
    VT: str = None
    PI: int = None
    EX: int = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class Area(RowIdentification):
    NA: int = None
    AC: str = None
    LA: int = None
    AN: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class EamResourceassocation(RowIdentification):
    NA: int = None
    VN: str = None
    PS: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class ParaRef(RowIdentification):
    VN: str = None
    DT: str = None
    NI1: int = None
    PI: int = None
    VC: int = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class MsrRef(RowIdentification):
    MP: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class PbvOpjpath(RowIdentification):
    NA: int = None
    LB: str = None
    FN: str = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class GwyAccEam(RowIdentification):
    MP: str = None
    LEN: int = None
    PARA: list = None
    END: int = None

    def string(self) -> str:
        gwy_string = self._get_string_from_dict_with_dict(self.PARA)
        normal_string = self._get_string_from_dict_with_string(self.dict(exclude={"PARA", "END"}))
        return f"{normal_string};{gwy_string};{self.END}"


class GwyAccMsr(RowIdentification):
    MP: str = None
    LEN: int = None
    PARA: list = None
    END: int = None

    def string(self) -> str:
        gwy_string = self._get_string_from_dict_with_dict(self.PARA)
        normal_string = self._get_string_from_dict_with_string(self.dict(exclude={"PARA", "END"}))
        return f"{normal_string};{gwy_string};{self.END}"


class Hw2Blob(RowIdentification):
    DTMN: int = None
    QC: int = None
    DTMC: tuple = None

    def string(self) -> str:
        hex_string = self._get_string_ascii_hex(self.DTMC)
        normal_string = self._get_string_from_dict_with_string(self.dict(exclude={"DTMC"}))
        return f"{normal_string};{hex_string}"


class IoDescription(RowIdentification):
    CN: str = None
    IO: int = None
    DT: int = None
    UB: int = None
    B: int = None
    BL: int = None
    VN: str = None
    C: str = None
    NI1: int = None
    NI2: int = None
    NI3: int = None
    NI4: int = None
    NI5: int = None
    NI6: int = None
    NI7: int = None
    NI8: int = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


class Hw2Node(RowIdentification):
    RID: str = None
    NI1: str = None
    NI2: str = None
    NI3: str = None
    NI4: str = None
    MT: str = None
    LB: str = None
    NI5: str = None
    NI6: str = None
    NI7: str = None
    NI8: str = None
    NI9: str = None
    NI10: str = None
    NI11: str = None
    NI12: str = None
    NI13: str = None
    NI14: str = None
    NI15: str = None
    MP: str = None
    PS: str = None
    NA: int = None

    def string(self) -> str:
        return self._get_string_from_dict_with_string(self.dict())


__FREELANCE_IDENTIFICATION = {
    "[MSR:RECORD]": (MsrRec, MsrRecordDict),
    "[UID:ACCMSR]": (UidAcc, UidAccDict),
    "[PARA:PARADATA]": (ParaData, ParaDataDict),
    "[PB:NODE]": (PBNode, PbNodeDict),
    "[EAM:RECORD]": (EamRecord, EamRecordDict),
    "[AREA]": (Area, AreaDict),
    "[EAM:RESOURCEASSOCIATION]": (EamResourceassocation, EamResourceDict),
    "[LAD:PARA_REF]": (ParaRef, ParaRefDict),
    "[LAD:MSR_REF]": (MsrRef, MsrRefDict),
    "[PBV:OBJPATH]": (PbvOpjpath, PbvObjpathDict),
    "[GWY:ACCEAM]": (GwyAccEam, GwyDict),
    "[GWY:ACCMSR]": (GwyAccMsr, GwyDict),
    "[HW2_BLOB]": (Hw2Blob, Hw2BlobDict),
    "[BEGIN_IODESCRIPTION]": (IoDescription, BeginIODescriptionDict),
    "[HW2_NODE]": (Hw2Node, Hw2NodeDict)
    }


def row_identificator(row: tuple[str]) -> RowIdentification:
    if row[0] not in __FREELANCE_IDENTIFICATION.keys():
        raise AttributeError('cant find identificator!')
    (id, CreateDict) = __FREELANCE_IDENTIFICATION[row[0]]
    row_dict = CreateDict().merge_dict(row)
    return id(**row_dict)
