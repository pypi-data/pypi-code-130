# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

import ftplib
import os
import sys

from varuploader.config import CACHEDIR


def connect_ftp(ftp_user_name, ftp_passwd,
                ftp_host_name="ftp.variscite.com", ftp_timeout=100):
    try:
        ftp = ftplib.FTP(ftp_host_name, timeout=ftp_timeout)
        ftp.login(user=ftp_user_name, passwd=ftp_passwd)
    except ftplib.all_errors as error:
        sys.stderr.write(f"Fail to connect to {ftp_host_name}: {error}\n")
        return False, error
    return ftp, True


def retrieve_remote_file(ftp, file_name, remote_path):
    local_file = os.path.join(CACHEDIR, file_name)
    if os.path.exists(local_file):
        os.remove(local_file)
    try:
        ftp.cwd(remote_path)
        with open(local_file, "wb") as f:
            res = ftp.retrbinary(f"RETR {file_name}", f.write, blocksize=1024)
            if not res.startswith("226 Transfer complete"):
                os.remove(local_file)
                return False
    except ftplib.all_errors as error:
        sys.stderr.write(f"[FTP]: Fail to retrieve '{local_file}': {error}\n")
        ftp.quit()
        return False
    ftp.quit()
    return local_file


def stor_remote_file(ftp, file_name, file_path, remote_path):
    try:
        ftp.cwd(remote_path)
        with open(file_path, "rb") as fp:
            res = ftp.storbinary(f"STOR {file_name}", fp, blocksize=2048)
            if not res.startswith("226 Transfer complete"):
                return False
    except ftplib.all_errors as error:
        sys.stderr.write(f"[FTP]: Fail to upload '{file_name}': {error}\n")
        ftp.quit()
        return False
    ftp.quit()
    return True
