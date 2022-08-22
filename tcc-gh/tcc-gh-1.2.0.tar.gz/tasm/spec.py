types = {
    10: "Integer",
    11: "Bit",  # bool/bit
    12: "Address",  # register pointer
}

instructions: dict[str, list[int]] = {
    "mov": [
        10,  # id
        2,  # argc
        10,  # argv[1]
        12,  # argv[2]
    ],
    "free": [11, 1, 12],
    "ret": [12, 1, 12],
    "cpy": [13, 2, 12, 12],
    "add": [14, 2, 12, 12],
    "@label": [15, 1, 10],
    "jmp": [16, 1, 10],
}
