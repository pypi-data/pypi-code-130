from .bc import *
from .exceptions import *


def intc_to_val(type: int, val: int) -> int:
    rval = None
    # integer
    if type == 10:
        rval = val - 10

    # bit/bool
    elif type == 11:
        rval = val - 11

    # Address
    elif type == 12:
        rval = val - 12

    else:
        raise TVM_ValueDecodeError()
    return rval


class Register:
    __reg: dict[int]

    def __init__(self) -> None:
        self.__reg = {}

    def set(self, p: int, v):
        try:
            self.__reg[p] = v
        finally:
            print(f"(mem) {hex(p)} <- {v}")

    def get(self, p: int) -> int:
        try:
            return self.__reg[p]
        except KeyError:
            raise TVM_RegisterIsEmptyError(p)
        finally:
            print(f"(mem) {hex(p)} ->")

    def new(self, v=0) -> int:
        na = self.__new_addr()
        self.__reg[na] = v
        return na

    def pop(self, p: int) -> None:
        try:
            self.__reg.pop(p)
        except KeyError:
            raise TVM_RegisterIsEmptyError(p)
        finally:
            print(f"(mem) {hex(p)} <-")

    def __new_addr(self) -> int:
        s = True
        addr = 0
        used = self.__reg.keys()
        while s:
            if addr in used:
                addr += 1
        return addr


class Program:
    register: Register
    running: bool
    retcode: int
    pc: int
    currlabel: int
    labels: dict[int, list[IntCode]]

    def __init__(self, vms: str) -> None:
        self.hc = read_hc_file(vms)
        self.register = Register()

    def eval(self, ic: IntCode) -> None | IntCode:
        try:
            ins_id = ic[0]
            ins_args = ic[1:]

            if ins_id == 10:
                self.ins_mov(*ins_args)

            elif ins_id == 11:
                self.ins_free(*ins_args)

            elif ins_id == 12:
                self.ins_ret(*ins_args)

            elif ins_id == 13:
                self.ins_cpy(*ins_args)

            elif ins_id == 14:
                self.ins_add(*ins_args)

            elif ins_id == 15:
                self.ins_def_label(*ins_args)

            elif ins_id == 16:
                self.ins_jmp(*ins_args)

            else:
                raise TVM_UnknownInstructionError(ins_id)
            return None

        except TVM_Error as e:
            self.retcode = 1
            self.running = False
            print(f"(Error) ({str(self.pc)}) {e}")

        except RecursionError:
            return

    def run_label(self, label: int) -> None:
        try:
            code = self.labels[label]
        except IndexError:
            raise TVM_UnknownLabelError(label)

        for ins in code:
            self.currlabel = label
            self.eval(ins)
        self.currlabel = 0

    def run(self) -> int:
        self.pc = 0
        self.running = True
        self.retcode = 0
        self.currlabel = 0
        self.labels = {0: []}
        self.code = hexc_to_intc(self.hc)
        _ins: IntCode = []

        for _part in self.code:
            if _part == 0x0:
                self.pc += 1
                self.labels[self.currlabel].append(_ins)
                self.eval(_ins)
                _ins = []

                if not self.running:
                    break

            else:
                _ins.append(_part)

        return self.retcode

    def ins_mov(self, _a: int, _b: int) -> None:
        _a = intc_to_val(10, _a)
        _b = intc_to_val(12, _b)
        self.register.set(_b, _a)

    def ins_free(self, _a: int) -> None:
        _a = intc_to_val(12, _a)
        self.register.pop(_a)

    def ins_ret(self, _a: int) -> None:
        _a = intc_to_val(12, _a)
        self.retcode = self.register.get(_a)
        self.running = False

    def ins_cpy(self, _a: int, _b: int) -> None:
        _a = intc_to_val(12, _a)
        _b = intc_to_val(12, _b)
        self.register.set(_b, self.register.get(_a))

    def ins_add(self, _a: int, _b: int) -> None:
        _a = intc_to_val(12, _a)
        _b = intc_to_val(12, _b)
        a = self.register.get(_a)
        b = self.register.get(_b)
        self.register.set(_a, a + b)

    def ins_def_label(self, _a: int) -> None:
        _a = intc_to_val(10, _a)
        self.currlabel = _a
        self.labels[_a] = []

    def ins_jmp(self, _a: int) -> None:
        _a = intc_to_val(10, _a)
        self.run_label(_a)
