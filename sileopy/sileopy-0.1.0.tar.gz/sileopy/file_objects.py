# -*- coding: utf-8 -*-
"""
This method contains classes, methods and helper functions for file handling.
"""
# Python module imports
import logging
import hashlib
import os
import shutil
import platform
from datetime import datetime

# Local module imports
from sileopy.common_functions import tracelog


# Logger setup
logger = logging.getLogger(__name__)


@tracelog
def get_csv_files_in_dir(path):
    """
    Scan given `path` for files with extension .csv and return list with
    file names of any files found

    Parameters
    ----------
    path : str
        Directory path to scan for CSV files

    Returns
    -------
    List of filenames found in given `path`
    """
    csv_files = []

    for entry in os.scandir(path):
        if entry.is_file():
            if entry.name[-4:] == '.csv':
                csv_files.append(entry.name)

    return csv_files


@tracelog
def get_sha256_file_hash(filename):
    """
    Calculate SHA-2 hash for given file.

    Parameters
    ----------
    filename: str
        Filename of the file to hash

    Returns
    -------
    String containing SHA-256 hash
    """
    algo = hashlib.sha256()

    with open(filename, 'rb') as file_to_hash:
        for chunk in iter(lambda: file_to_hash.read(128 * algo.block_size), b''):
            algo.update(chunk)

    return algo.hexdigest()


@tracelog
def move_file(path, filename, destination):
    """
    Move file with given `filename` in given `path` to `destination`.

    Parameters
    ----------
    path : str
        Path to directory containing files to be moved
    filename : str
        Filename of file to move
    destination : str
        Destination folder

    Returns
    -------
    True on success
    """
    if destination[-1] not in ['/', '\\']:
        destination = destination + '/'

    # Changing directory facilitates reading files from network paths
    working_dir = os.getcwd()
    os.chdir(os.path.dirname(path))

    if os.path.isdir(destination):
        shutil.move(path + filename, destination + filename)
    else:
        logger.error("File/path error")
        raise FileNotFoundError

    # Return to proper working directory
    os.chdir(working_dir)

    return True


@tracelog
def move_files(path, filenames, destination):
    """
    Move files with given `filenames` in given `path` to `destination`.

    Parameters
    ----------
    path : str
        Path to directory containing files to be moved
    filenames : list of str
        Filename of file to move
    destination : str
        Destination folder

    Returns
    -------
    True on success
    """
    for filename in filenames:
        move_file(path, filename, destination)

    return True


@tracelog
def adjust_path_slashes(filepath):
    """
    Replace slashes with backslashes or vice versa depending on operating system
    and return the updated file path

    Parameters
    ----------
    filepath : str
        Path to a directory

    Returns
    -------
    new_filepath : str
        The updated path
    """
    if platform.system() == 'Windows':
        new_filepath = filepath.replace('/', '\\')
    else:
        new_filepath = filepath.replace('\\', '/')
    return new_filepath


@tracelog
def get_file_detail(filepath, filename, entity, origin):
    """
    Hash input file and return file details, i.e. hash-value, file name,
    origin and entity

    Parameters
    ----------
    filepath : string
        path to file to hash
    filename : string
        name of the file
    entity : string
        entity of the file
    origin : string
        origin of the file

    Returns
    -------
    file_detail : dict
        Dictionary with file details
    """
    hash_value = get_sha256_file_hash(filepath)
    file_detail = {
        'filename': filename,
        'entity': entity,
        'filehash': hash_value,
        'origin': origin
    }
    return file_detail


@tracelog
def get_portfoliodatafile_prefix(creditor_name):
    """
    Create a string containing creditor name, current year, month, day and time.

    Parameters
    ----------
    creditor_name : str
        Name of the creditor

    Returns
    -------
    portfoliodatafile_prefix : str
        The prefix for the portfolio data file. 
    """
    datestamp = datetime.strftime(datetime.now(), '%Y-%m-%d-%H%M%S%f')[:-2]

    portfoliodatafile_prefix = 'portfolio_' + datestamp + '_' \
        + creditor_name.replace(' ', '_') + '_'
    
    return portfoliodatafile_prefix