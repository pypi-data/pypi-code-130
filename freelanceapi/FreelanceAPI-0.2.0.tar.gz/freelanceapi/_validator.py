from pydantic import validator


class Identifcation(str):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_ID

    @classmethod
    def validate_ID(cls, v: str) -> str:
        print(v)
        return v


class LengthDataset(int):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_LEN

    @classmethod
    def validate_LEN(cls, v: int) -> int:
        print(v)
        return v


class NextElementAvailable(int):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_NA

    @classmethod
    def validate_NA(cls, v: int) -> int:
        print(v)
        return v


class MeasuringPoint(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_MP

    @classmethod
    def validate_MP(cls, v: str) -> str:
        print(v)
        return v


class ModuleType(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_MT

    @classmethod
    def validate_MT(cls, v: str) -> str:
        print(v)
        return v


class ShortText(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_MT

    @classmethod
    def validate_ST(cls, v: str) -> str:
        print(v)
        return v


class LongText(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_LT

    @classmethod
    def validate_LT(cls, v: str) -> str:
        print(v)
        return v


class AreaDefinition(int):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_AD

    @classmethod
    def validate_AD(cls, v: int) -> int:
        print(v)
        return v


class StatusBit(int):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_SB

    @classmethod
    def validate_SB(cls, v: int) -> int:
        print(v)
        return v


class VariableName(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_VN

    @classmethod
    def validate_VN(cls, v: str) -> str:
        print(v)
        return v


class DataTyp(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_DT

    @classmethod
    def validate_DT(cls, v: str) -> str:
        print(v)
        return v


class VariableText(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_VT

    @classmethod
    def validate_VT(cls, v: str) -> str:
        print(v)
        return v


class ProcessImage(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_PI

    @classmethod
    def validate_PI(cls, v: str) -> str:
        print(v)
        return v


class ExportedVariable(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_EV

    @classmethod
    def validate_EV(cls, v: str) -> str:
        print(v)
        return v


class VariableOrConst(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_VC

    @classmethod
    def validate_VC(cls, v: str) -> str:
        print(v)
        return v


class Fbs(str):

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_FB

    @classmethod
    def validate_FB(cls, v: str) -> str:
        print(v)
        return v


class Libary:

    @classmethod
    def __get_validators__(cls) -> None:
        yield cls.validate_LB

    @classmethod
    def validate_LB(cls, v: str) -> str:
        print(v)
        return v


class DtmNumber():
    pass


class DtmConfig():
    pass


class QuantityCounter():
    pass


class FunctionName():
    pass


class ChannelName():
    pass


class InputOutput():
    pass


class UsedByte():
    pass


class Bit():
    pass


class ByteLength():
    pass


class Commend():
    pass


class AreaChar():
    pass


class LengthAreaText():
    pass


class AreaName():
    pass


class ParaSettings():
    pass

class NoIdear():
    pass
