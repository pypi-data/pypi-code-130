# -*- coding: utf-8 -*-
"""
This module fetches new portfolio files from a FTP server to a local directory,
and then moves the files to another directory on the FTP.

Flow:
1. Connect to SFTP server
2. Download files in remote_dir to local_dir
3. Move downloaded files to remote_dir_destination
"""

# Python module imports
import logging
import shutil
import os
from stat import S_ISDIR, S_ISREG
from datetime import datetime

# 3rd party module imports
import paramiko

# Local module imports


# Logger setup
logger = logging.getLogger(__name__)


# All paths to directories must have ending forwardslash
# Always use forwardslash in paths, even in a Windows environment

def is_file(sftp, filename):
    """
    Check if given filename is a file
    """
    try:
        return S_ISREG(sftp.stat(filename).st_mode)
    except IOError:
        return False


def is_dir(sftp, filename):
    """
    Check if given filename is a directory
    """
    try:
        return S_ISDIR(sftp.stat(filename).st_mode)
    except IOError:
        return False


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


def get_new_ftp_files(
    remote_dir,
    remote_dir_destination,
    local_dir,
    SFTP_HOST,
    SFTP_USER,
    SFTP_PASSWORD,
    SFTP_PORT
    ):
    """
    Download new files from remote_dir at SFTP_HOST to local_dir.
    Files downloaded will be moved remotely to remote_dir_destination

    Parameters
    ----------
    remote_dir : str
        Path to directory containing files to be downloaded
    remote_dir_destination : str
        Destination directory at SFTP_HOST
    local_dir : str
        Local destination directory
    SFTP_HOST : str
        Hostname of the FTP-server
    SFTP_USER : str
        Username of the FTP-account
    SFTP_PASSWORD : str
        Password of the FTP-account

    Returns
    -------
    List of fetched files on success, otherwise False
    """
    # Check FTP-settings
    if not all([SFTP_HOST, SFTP_USER, SFTP_PASSWORD, SFTP_PORT]):
        logger.error("Cannot connect to FTP-server: Missing FTP-settings.")
        return False

    fetched_files = []
    passw = SFTP_PASSWORD

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logger.info("Connecting to %s as %s", SFTP_HOST, SFTP_USER)
    ssh.connect(SFTP_HOST, username=SFTP_USER, password=passw, port=SFTP_PORT)
    sftp = ssh.open_sftp()

    sftp.chdir(remote_dir_destination)
    existing_files = sftp.listdir()
    timestamp = datetime.strftime(
            datetime.now(),
            '%Y-%m-%d-%H%M%S'
        )

    sftp.chdir(remote_dir)
    files = sftp.listdir()

    logger.debug("New files to get: %s", files)
    
    for remote_file in files:
        if is_file(sftp, remote_file):
            # Fetch the file to the local directory
            logger.info("Downloading %s", remote_file)
            sftp.get(remote_file, local_dir + remote_file)

            fetched_files.append(remote_file)

            # Move the remote file after fetch, change filename if file exist
            logger.info("Moving " + remote_file + " on server to " + remote_dir_destination)
            if remote_file in existing_files:
                sftp.rename(remote_dir + remote_file, remote_dir_destination + remote_file + '.' + timestamp)
            else:
                sftp.rename(remote_dir + remote_file, remote_dir_destination + remote_file)

    logger.info("Closing connection")
    sftp.close()
    ssh.close()

    return fetched_files
