import sys
"""
convertbin - the standard binary conversion module
"""
def text_to_bits(text, encoding=sys.getdefaultencoding(), errors='surrogatepass'):
    """
    Translates text to binary (base 2)
    """
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding=sys.getdefaultencoding(), errors='surrogatepass'):
    """
    Translates base 2, or binary, to text
    """
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'
def unicode_table(sr, er):
    """
    Unicode range from table specified. Example: unicode_table(0x0, 0x100).
    This will provide the ASCII range.
    Note that the ending character will not be included
    """
    table = []
    for i in range(int(sr), int(er)):
        table.append(chr(i))
    return table
