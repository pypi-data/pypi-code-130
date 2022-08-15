import os


def exists(filename):
    return os.path.exists(filename)


def rename(src, dst):
    return os.rename(src, dst)


def mkdirs(filename, all_dir=False, mode=0o755):
    dirs = os.path.dirname(filename) if not all_dir else filename
    if not exists(dirs):
        os.makedirs(dirs, mode=mode)
    return True


def read_all(filename):
    with open(filename) as f:
        data = f.read()

    return data


def write_all(filename, content):
    with open(filename, 'w') as f:
        length = f.write(content)

    return length


def safe_write_all(filename, content):
    tmp_filename = f'{filename}.tmp'
    length = write_all(tmp_filename, content)
    if length is not None and length > 0:
        rename(tmp_filename, filename)

    return length
