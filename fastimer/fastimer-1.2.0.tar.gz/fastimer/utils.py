#!/usr/bin/env python3

import datetime


def get_time_difference(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> tuple:

    seconds_per_hour = 3600
    seconds_per_minute = 60

    seconds = (end_date - start_date).total_seconds()

    hours = int(seconds // seconds_per_hour)
    minutes = int(seconds % seconds_per_hour // seconds_per_minute)

    return hours, minutes


def aligned_string(title: str, value: str, width: int = 15) -> str:

    if len(title) > width:
        width = len(title)

    title = f"{title}:".ljust(width)

    return f"{title} {value}"


def print_with_alignment(title: str, value: str, width: int = 15) -> None:

    title = f"{title}:".ljust(width)

    print(f"{title} {value}")


def get_active_fast(fasts: list) -> dict | None:

    return fasts[-1] if len(fasts) > 0 and fasts[-1].get("stopped") is None else None


def is_fast_stopped(fast: dict) -> bool:

    return fast.get("stopped") is not None


def is_fast_completed(fast: dict) -> bool:

    hours_in_fast = get_fast_length(fast)[0]

    return fast.get("length") <= hours_in_fast


def get_fast_length(fast: dict) -> tuple:

    started = fast["started"]
    stopped = fast.get("stopped")

    if stopped is not None:
        result = get_time_difference(started, stopped)
    else:
        result = 0, 0

    return result
