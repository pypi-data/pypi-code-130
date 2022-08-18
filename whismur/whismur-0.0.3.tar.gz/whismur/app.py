import asyncio
import io
import re
from pathlib import Path
from typing import *

import aiohttp
import psutil
from mousse import Dataclass, asclass, load_config, init_logger
from typer import Argument, Option, Typer

from .constants import BASE_DIR

__all__ = ["app"]

logger = init_logger(log_dir="logs")


class Telebot(Dataclass):
    access_token: str
    chat_id: int

    @property
    def end_point(self):
        return f"https://api.telegram.org/bot{self.access_token}"

    async def send_message(self, *args, **kwargs):
        buffer = io.StringIO()
        print(*args, end="", file=buffer)
        text = buffer.getvalue()

        api = "/".join((self.end_point, "sendMessage"))
        async with aiohttp.ClientSession() as session:
            params = {"chat_id": self.chat_id, "text": text}
            async with session.get(api, params=params) as response:
                print(response.status)


app = Typer()


@app.command()
def info():
    print("Whismur")


@app.command()
def send_msg(
    msg: str = Argument(..., help="Message"),
    config_path: Path = Option(
        BASE_DIR / "config" / "telebot.yaml", help="Path to config file"
    ),
):
    telebot: Telebot = asclass(
        Telebot, load_config("monitor_pid", path=config_path.as_posix())
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(telebot.send_message(msg))


@app.command()
def monitor_pid(
    pid_path: Path = Argument(..., help="Pid file to monitor"),
    config_path: Path = Option(
        BASE_DIR / "config" / "telebot.yaml", help="Path to config file"
    ),
    interval: int = Option(1, help="Check interval"),
):
    telebot: Telebot = asclass(
        Telebot, load_config("monitor_pid", path=config_path.as_posix())
    )

    async def check_pid(pid_path: Path):
        stopped_pids = set()

        while True:
            logger.info("Check pid from", pid_path.as_posix())
            pids = set()

            if pid_path.exists():
                with open(pid_path) as fin:
                    for line in fin:
                        line = line.strip()
                        pid, path = line.split("\t")
                        if re.fullmatch("\d+", pid):
                            pids.add((int(pid), path))

            for pid, path in pids:
                if pid in stopped_pids:
                    continue

                if psutil.pid_exists(pid):
                    continue

                await telebot.send_message(
                    f"Process [{pid}] of [{path}] is either stopped or not found"
                )
                stopped_pids.add(pid)

            await asyncio.sleep(interval)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(check_pid(pid_path))
    except KeyboardInterrupt:
        logger.info("Force stop")
        loop.stop()
