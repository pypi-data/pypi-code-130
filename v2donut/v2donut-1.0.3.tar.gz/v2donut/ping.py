from __future__ import annotations

from threading import Thread, Lock

import pythonping

from v2donut.appsettings import AppSettings
from v2donut.subscription import VmessShare


best: tuple[VmessShare, float] | None = None
lock = Lock()


def ping(vs: list[VmessShare], settings: AppSettings, mode="ping") -> VmessShare:
    ts = []

    print(f"正在测试 {mode}", end='')

    for v in vs:
        if not v.host or v.host.isspace():
            continue

        t = Thread(
            target=pings,
            args=(
                v,
                settings.timeout,
                settings.count,
            ),
        )

        t.start()
        ts.append(t)

    for t in ts:
        t.join()

    v = best[0]

    print(f"\n最快的服务器是 [{v.ps} - {v.host}], 时间={best[1]}ms")

    return v


def pings(v: VmessShare, timeout: int, count: int):
    res = pythonping.ping(v.host, timeout, count)
    if not res.success():
        return

    print(">", end="")

    ms = res.rtt_avg_ms

    global best
    try:
        lock.acquire()
        if best is None or ms < best[1]:
            best = (v, ms)
    finally:
        lock.release()
