# Copyright 2022 Variscite LTD
# SPDX-License-Identifier: BSD-3-Clause

import itertools
import os

WINDOW_T = "Recovery SD Card Uploader Tool"
WINDOW_W = 1280 
WINDOW_H = 720

UNITS = ("B", "KiB", "MiB", "GiB")

SOFTWARE = "Software"
OS_YOCTO = "yocto"
OS_DEBIAN = "debian"
OS_B2QT = "b2qt"

VAR_UPLOADER_FOLDER = "varuploader"
CACHEDIR = os.path.join(os.environ['HOME'], ".cache", VAR_UPLOADER_FOLDER)

VARISCITE_LOGO_PATH = "assets/variscite.png"

MX8M    = "DART-MX8M"
MX8MM   = "DART-MX8M-MINI"
MX8MP   = "DART-MX8M-PLUS"

YAML_CHANGELOG_MX8M     = "mx8m-recovery-sd-changelog.yml"
YAML_CHANGELOG_MX8MM    = "mx8mm-recovery-sd-changelog.yml"
YAML_CHANGELOG_MX8MP    = "mx8mp-recovery-sd-changelog.yml"

MX8_SOM_DARTS = [MX8M, MX8MM, MX8MP]

MX8     = "VAR-SOM-MX8"
MX8X    = "VAR-SOM-MX8X"
MX8MN   = "VAR-SOM-MX8M-NANO"

YAML_CHANGELOG_MX8      = "mx8-recovery-sd-changelog.yml"
YAML_CHANGELOG_MX8X     = "mx8x-recovery-sd-changelog.yml"
YAML_CHANGELOG_MX8MN    = "mx8mn-recovery-sd-changelog.yml"

MX8_SOM_VARS = [MX8, MX8X, MX8MN]

MX8_YAML_CHANGELOG_FILES = {
         MX8M : YAML_CHANGELOG_MX8M,
         MX8MM : YAML_CHANGELOG_MX8MM,
         MX8MP : YAML_CHANGELOG_MX8MP,
         MX8 : YAML_CHANGELOG_MX8,
         MX8X : YAML_CHANGELOG_MX8X,
         MX8MN : YAML_CHANGELOG_MX8MN}

VAR_SYSTEM_ON_MODULES = list(itertools.chain(MX8_SOM_DARTS, MX8_SOM_VARS))

VAR_SYSTEM_ON_MODULES_NAME = {
        MX8M : "mx8m",
        MX8MM : "mx8mm",
        MX8MP : "mx8mp",
        MX8 : "mx8",
        MX8X : "mx8x",
        MX8MN : "mx8mn"
}

VAR_OS = ["yocto", "debian", "b2qt"]
