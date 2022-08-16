# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

from datetime import datetime
from hashlib import sha224
import math
import os

from varuploader.config import UNITS
from varuploader.config import SOFTWARE
from varuploader.config import OS_B2QT
from varuploader.config import OS_DEBIAN
from varuploader.config import OS_YOCTO
from varuploader.config import VAR_SYSTEM_ON_MODULES_NAME


def get_current_date(date_fmt):
    return datetime.today().strftime(date_fmt)

def calculate_sha224_hash(file_name):
    with open(file_name, "rb") as file:
        data = file.read()
    return sha224(data).hexdigest()

def get_file_size(file_name):
    size_bytes = os.path.getsize(file_name)
    if size_bytes == 0:
        return "0B"
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    size_fmt = f"{s} {UNITS[i]} ({size_bytes:,} bytes)"
    return size_fmt

def check_image_file_extension(image_name):
    return True if image_name.endswith("img.gz") else False

def _basename(full_path):
    return os.path.basename(os.path.normpath(full_path))

def get_som_folder_path(som_name, os_type):
    return {OS_YOCTO   : os.path.join(som_name, SOFTWARE),
            OS_DEBIAN  : os.path.join(som_name, SOFTWARE, OS_DEBIAN),
            OS_B2QT    : os.path.join(som_name, SOFTWARE, OS_B2QT)}[os_type]

def get_release_name(module, yaml_dict):
    module_name = VAR_SYSTEM_ON_MODULES_NAME[module]
    yocto_release_name = yaml_dict['Release']['Yocto Release'].split()[0].lower()
    yocto_release_version = yaml_dict['Release']['Yocto Release'].split()[1]
    yocto_version = yaml_dict['Release']['Yocto Version']
    android_release_version =  yaml_dict['Release']['Android Release']
    android_version = yaml_dict['Release']['Android Version']

    return f"{module_name}__yocto-{yocto_release_name}-{yocto_release_version}-{yocto_version}__android-{android_release_version}-{android_version}.img.gz"
