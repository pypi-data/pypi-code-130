def align_int(num: str, align_bytes: int) -> int:
    align_off = num % align_bytes
    if align_off == 0:
        return num
    return num + (align_bytes - align_off)
