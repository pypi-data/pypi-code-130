import struct

def deserialize_int(int_val_repr):
    return int.from_bytes(int_val_repr, 'little', signed=True)


def deserialize_int32(int_val_repr):
    return int.from_bytes(int_val_repr, 'little', signed=True)


def serialize_int(int_val_arg):
    return int_val_arg.to_bytes(8, byteorder='little', signed=True)


def serialize_int32(int_val_arg):
    return int_val_arg.to_bytes(4, byteorder='little', signed=True)


def deserialize_dbl(dbl_val_repr):
    result = struct.unpack('<d', dbl_val_repr)[0]
    return result


def serialize_dbl(dbl_val_arg):
    result = struct.pack('<d', dbl_val_arg)
    return result
