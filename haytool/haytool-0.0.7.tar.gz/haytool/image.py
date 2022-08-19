import random


def hex_to_rgb(hex):
    hex = hex.lstrip('#')
    hlen = len(hex)
    hlen_div = int(hlen / 3)
    return tuple(int(hex[i : i + hlen_div], 16) for i in range(0, hlen, hlen_div))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def random_hex():
    r = lambda: random.randint(0, 255)
    x = '#%02X%02X%02X' % (r(), r(), r())
    return x
