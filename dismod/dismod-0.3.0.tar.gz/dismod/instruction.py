from __future__ import annotations

from dis import Instruction, get_instructions
from types import CodeType
from typing import Sequence

from dismod.utils import neighborhood, search_key_in_iterable


def _extract_import_instructions(
    instructions: list[Instruction],
) -> list[Instruction]:
    """ """
    import_instructions = []
    for instruction in instructions:
        if instruction.opcode in (84, 108, 109):
            import_instructions.append(instruction)

    return import_instructions


def _convert_codeblocks_instructions(
    instructions: list[Instruction],
) -> list[Instruction]:
    """ """
    converted_instructions = []
    for instruction in instructions:
        if instruction.opcode == 100 and isinstance(
            instruction.argval,
            CodeType,
        ):
            extracted_instructions = _extract_import_instructions(
                list(get_instructions(instruction.argval)),
            )
            converted_instructions.extend(extracted_instructions)

    return converted_instructions


def get_instructions_from_file(filepath: str) -> list[Instruction]:
    contents = None
    with open(filepath) as file:
        contents = file.read()

    return list(get_instructions(contents))  # type: ignore


def get_import_instructions(
    instructions: list[Instruction],
) -> list[Instruction]:
    normalized_codeblocks = _convert_codeblocks_instructions(
        instructions=instructions,
    )
    normalized_codeblocks.extend(instructions)
    return _extract_import_instructions(instructions=normalized_codeblocks)


def _check_from_statement(current: int, following: int) -> bool:
    """ """
    return (current == 108 and following == 109) or (
        current == 108 and following == 84
    )


def _check_import_from_statement(
    previous: int,
    current: int,
    following: int | None,
) -> bool:
    """ """
    return (
        (current == 109 and following == 109)
        or (current == 84 and previous == 108)
        or (current == 109 and previous == 108)
    ) or (current == 109 and following is None)


def _check_single_import_statement(current: int, following: int) -> bool:
    """ """
    return (current == 108 and following == 108) or (
        current == 108 and following is None
    )


def parse_instructions(
    instructions: list[Instruction],
) -> list[dict[str, Sequence[str] | None]]:
    """ """
    current_from_statement_name = ""
    parsed_instructions: list[dict[str, Sequence[str] | None]] = []
    for previous, current, following in neighborhood(iterable=instructions):
        # Try to handle from statements import name
        if following and _check_from_statement(
            current=current.opcode,
            following=following.opcode,
        ):
            # Associate the argval from the current instruction being analyzed
            # If we find a '' in the argval property, it means that we are
            # handling a from . import <something>
            current_from_statement_name = (
                current.argval if current.argval else "."
            )

            _, has_from_statement = search_key_in_iterable(
                key="from_statement",
                value=current_from_statement_name,
                iterable=parsed_instructions,
            )
            if not has_from_statement:
                # Initialize a basic structure for the from/import statements
                parsed_instructions.append(
                    {
                        "from_statement": current_from_statement_name,
                        "import_statements": [],
                    },
                )

        # Try to handle import statements that are derivade from a
        # from statement
        if _check_import_from_statement(
            previous=previous.opcode if previous else None,
            current=current.opcode,
            following=following.opcode if following else None,
        ):
            index, _ = search_key_in_iterable(
                key="from_statement",
                value=current_from_statement_name,
                iterable=parsed_instructions,
            )
            parsed_instructions[index]["import_statements"].append(
                current.argval if current.argval else "*",
            )

        # Handle single import statements, no matter where they are
        if _check_single_import_statement(
            current=current.opcode,
            following=following.opcode if following else None,
        ):
            parsed_instructions.append(
                {
                    "from_statement": None,
                    "import_statements": [current.argval],
                },
            )

    return parsed_instructions
