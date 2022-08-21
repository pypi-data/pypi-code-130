"""
JPG: FF D8 FF
PNG: 89 50 4e 47
GIF: 47 49 46 38
"""

__version__ = '0.0.3'

import os
from typing import NamedTuple

# 定义图片格式
IMAGE = NamedTuple('IMAGE', [('name', str), ('h1', int), ('h2', int)])

# 声明图片种类
images = [
    IMAGE('jpg', 0xff, 0xd8),
    IMAGE('png', 0x89, 0x50),
    IMAGE('gif', 0x47, 0x49),
]

# 定义异或结果类型
XOR = NamedTuple('XOR', [('xor', int), ('name', str)])


def get_xor(b: bytes) -> XOR:
    """获取异或值"""
    for image in images:
        x1 = image.h1 ^ b[0]
        x2 = image.h2 ^ b[1]
        if x1 == x2:
            # print(image.name, x1)
            return XOR(x1, image.name)
    raise '未匹配到图片类型'


def decode_bytes(bs: bytes, xor: int) -> bytes:
    """解密数据"""
    rt = bytearray()
    for b in bs:
        rt.append(b ^ xor)
    return rt


def decode_image(in_image: str, out_dir: str):
    """解密文件"""
    with open(in_image, 'rb') as f:
        xor = get_xor(f.read(2))
        f.seek(0)
        in_name = os.path.split(f.name)[1]
        out_name = os.path.join(out_dir, f'{os.path.splitext(in_name)[0]}.{xor.name}')
        if not os.path.exists(out_name):
            with open(out_name, 'wb') as w:
                w.write(decode_bytes(f.read(), xor.xor))
        return os.path.basename(out_name)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='解密微信加密图片文件',
        epilog=f'wedat({__version__}) by foyou(https://github.com/foyoux/foyou-wedat)'
    )
    parser.add_argument('file', nargs='*', help='微信加密 .dat 文件，可任意多个')
    parser.add_argument('-v', '--version', dest='version', help='show wedat version', action="store_true")
    parser.add_argument('-d', '--dir', dest='dir', type=str, help='folder of dat files')
    parser.add_argument('-o', '--out', dest='out', type=str, default='.', help='output folder')
    args = parser.parse_args()

    if args.version:
        print('wedat version', __version__)
        return

    files = args.file
    folder = args.dir
    output = args.out

    if len(files) == 0 and folder is None:
        parser.print_usage()
        return

    # 处理 files
    for file in files:
        x = decode_image(file, output)
        print(x)

    f: os.DirEntry
    for f in os.scandir(folder):
        if f.name.endswith('.dat'):
            x = decode_image(f.path, output)
            print(x)
