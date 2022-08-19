import os

from constant import FILE_TYPE, FILE_IGNORE, FILE_EXT_IGNORE

def organize_files():
    """
    Organize files in the current directory.
    """
    for file_format in FILE_TYPE.keys():
        try:
            os.mkdir(file_format)
        except FileExistsError:
            pass
    # list all files in current directory
    for file in os.listdir():
        # get file extension
        file_ext = os.path.splitext(file)[1]
        # check if file is in ignore list
        if file in FILE_IGNORE or file_ext in FILE_EXT_IGNORE:
            continue
        for file_format in FILE_TYPE.keys():
            if file_ext in FILE_TYPE[file_format]:
                os.rename(file, file_format + "/" + file)
                break
        else:
            os.rename(file, "other/" + file)

