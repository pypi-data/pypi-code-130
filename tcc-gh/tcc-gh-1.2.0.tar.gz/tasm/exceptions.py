class TVM_Error(Exception):
    """Base class for tvm errors"""

    msg: str

    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return str(self)


class TASM_Error(Exception):
    """Base class for tasm errors"""

    msg: str

    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return str(self)


class TVM_RegisterIsEmptyError(TVM_Error):
    """
    the register # does not contain a value."""

    def __init__(self, register: int) -> None:
        super().__init__(f"The register {register} does not contain a value.")


class TVM_ValueDecodeError(TVM_Error):
    """Could not decode value."""

    def __init__(self) -> None:
        super().__init__(f"Could not decode value. recompile or update tvm.")


class TVM_UnknownInstructionError(TVM_Error):
    """"""

    def __init__(self, instruction: int) -> None:
        super().__init__(
            f"Unknown instruction '{hex(instruction)}:{str(instruction)}'."
        )


class TVM_UnknownLabelError(TVM_Error):
    def __init__(self, label: int) -> None:
        super().__init__(f"The label '{hex(label)}:{str(label)}' is not defined.")


class TASM_UnknownTypeError(TASM_Error):
    """Unknown type"""

    def __init__(self, type: int) -> None:
        super().__init__(f"Unknown type '{hex(type)}:{type}'.")


class TASM_ArgumentError(TASM_Error):
    """"""

    def __init__(self, instruction: str, argc: int) -> None:
        super().__init__(f"{instruction} requires {str(argc)} arguments.")


class TASM_UnknownInstructionError(TASM_Error):
    """"""

    def __init__(self, instruction: str) -> None:
        super().__init__(f"Unknown instruction '{instruction}'.")


class TASM_IntSizeToBigError(TASM_Error):
    def __init__(self) -> None:
        super().__init__(f"Number to big. Integers must be in range 0-245.")
