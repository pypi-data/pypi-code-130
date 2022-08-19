from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from v2donut.appsettings import AppSettings
from v2donut.ping import ping
from v2donut.subscription import fetch
from v2donut.utils import get_default_conf
from v2donut.v2conf import gen_v2conf

conf_file = Path.home() / "v2donut.json"


def helpme():
    print("{:<16} {}".format("v2donut", "使用 Ping 测试延迟"))
    print("{:<16} {}".format("v2donut http", "使用 HTTP 测试延迟"))
    print("{:<16} {}".format("v2donut init", f"初始化程序配置, 配置文件路径: {conf_file}"))
    print("{:<16} {}".format("v2donut help", "获取帮助信息"))


def init_appsettings():
    if not os.path.exists(conf_file):
        with open(conf_file, "w") as cf:
            json.dump(get_default_conf(), cf, indent=4)


def main(mode: str):
    print(
        """
     ___   _             _   
 _ _|_  |_| |___ ___ _ _| |_ 
| | |  _| . | . |   | | |  _|
 \\_/|___|___|___|_|_|___|_|
    """
    )

    with open(conf_file) as conf:
        j = json.load(conf)
        setting = AppSettings(**j)

    vs = fetch(setting.url)
    best = ping(vs, setting, mode)
    gen_v2conf(best, setting)

    print(f"V2Ray 配置已调整为 [{best.ps} - {best.host}]")


def patched_main():
    args = sys.argv[1:]
    subcmd = "ping" if len(args) == 0 else args[0]

    if subcmd == "help":
        helpme()
    else:
        mode = subcmd
        init_appsettings()
        main(mode)
