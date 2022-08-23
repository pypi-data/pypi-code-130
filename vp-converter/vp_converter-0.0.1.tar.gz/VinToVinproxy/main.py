'This function takes VIN as input and returns hashed vin proxy as output which can be used further for data extraction from various buckets'


'author- Aman Kumar Gupta'
'contact- 8XXXXXXXX1'



def vin_to_proxy(vin):
    def _to_int(val, nbits):
        i = int(val, 16)
        if i >= 2 ** (nbits - 1):
            i -= 2 ** nbits
        return i

    initial_value=(_to_int(hex(0xcbf29ce484222325),64))
    salt_value=0x100000001b3
    for char in vin:
        xor_op=int(hex(ord(char)),16) ^ initial_value
        and_op=(_to_int(hex(xor_op), 64)*(1099511628211))%2**64
        initial_value=_to_int(hex(and_op),64)
    return (hex(and_op)[2:])
