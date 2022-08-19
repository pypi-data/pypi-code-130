import glog as log
import os


def create_new_folder(new_folder_name, directory=None):
    """Creates folder in directory

    Args:
        new_folder_name (str): folder name
        directory (str, optional): Directory. Defaults to None.

    Returns:
        str: New directory
    """
    if directory:
        filedir = directory
    else:
        filedir = os.getcwd()
    new_dir = os.path.join(filedir, new_folder_name)
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    return new_dir


def out_filepath(filepath, new_directory='', new_prefix='', new_suffix='', new_filetype='', new_filename=''):
    """Updates input filepath to output filepath.

    Args:
        filepath (str): Input filepath (include file name and extension)
        new_directory (str, optional): Path to new directory. Defaults to ''.
        new_prefix (str, optional): New file prefix. Defaults to ''.
        new_suffix (str, optional): New file suffix. Defaults to ''.
        new_filetype (str, optional): New file extension/filetype, if none then retains input file type. Defaults to ''.

    Returns:
        [str]: Output file path
    """
    directory, filename = os.path.split(filepath)
    head, ext = os.path.splitext(filename)
    if new_filename:
        head = new_filename
    if new_filetype:
        updated_filename = f'{new_prefix}{head}{new_suffix}.{new_filetype}'
    else:
        updated_filename = f'{new_prefix}{head}{new_suffix}{ext}'
    if new_directory:
        new_outfilepath = os.path.join(new_directory, updated_filename)
    else:
        new_outfilepath = os.path.join(directory, updated_filename)
    return new_outfilepath


def filesize(filepath):
    """Get file size. Output in bytes.

    Args:
        file (str): File path

    Returns:
        [str]: File size
    """

    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1000.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    return sizeof_fmt(os.path.getsize(filepath))
