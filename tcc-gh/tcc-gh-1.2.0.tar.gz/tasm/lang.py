from .exceptions import *
from .bc import *
from .spec import instructions


def read_int(s: str) -> int:
    try:
        return int(s)
    except:
        return int(s, 16)


class TASM_Value:
    intc: int

    def __init__(self, type: int, value: int) -> None:
        # Integer
        if type == 10:
            self.intc = 10 + value

        # Bit/Bool
        elif type == 11:
            if value <= 0:
                self.intc = 11
            else:
                self.intc = 12

        # Address
        elif type == 12:
            self.intc = 12 + value

        else:
            raise TASM_UnknownTypeError(type)


class TASM_Instruction:
    def __init__(self, id: int, argval: list[TASM_Value]) -> None:
        self.id = id
        self.argval = argval

    def hexc(self) -> HexCode:
        return intc_to_hexc(self.intc())

    def intc(self) -> IntCode:
        ins: IntCode = [self.id]

        for ii in self.argval:
            ins.append(ii.intc)

        ins.append(0x0)  # end of instruction
        return ins


class Parser:
    src: str
    ins: list[str]

    def __init__(self, src: str, isfile: bool = True) -> None:
        if isfile:
            with open(src, "r") as f:
                self.src = f.read()
        else:
            self.src = src

        # formatting
        self.src = self.src.strip()
        self.ins = self.src.split(";")
        i = 0
        for ii in self.ins:
            self.ins[i] = ii.strip("\n").strip()
            i += 1

    def gen_hc(self) -> HexCode:
        code: HexCode = []
        for instruction in self.ins:
            if instruction == "":
                continue
            parts = instruction.split(" ")
            if parts[0] == "//":
                continue

            elif parts[0] in instructions.keys():
                li = instructions[parts[0]]
                if len(parts) - 1 == li[1]:
                    args = parts[1:]
                    tasm_args: list[TASM_Value] = []
                    argi = 0
                    for ii in args:
                        tasm_args.append(TASM_Value(li[2 + argi], read_int(ii)))
                        argi += 1

                    ins = TASM_Instruction(li[0], tasm_args)
                    for ii in ins.hexc():
                        code.append(ii)

                else:
                    raise TASM_ArgumentError(parts[0], li[1])

            else:
                raise TASM_UnknownInstructionError(parts[0])
        return code
