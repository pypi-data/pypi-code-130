#!/usr/bin/env python3
# Copyright (c) 2022 4ndrs <andres.degozaru@gmail.com>
# SPDX-License-Identifier: MIT
# pylint: disable=missing-module-docstring
import sys
import psutil


def main():
    """Change the status of a given process (or a group of processes) sending
    SIGSTOP/SIGCONT.

        Usage:  psus firefox suspend
                psus firefox continue
    The script will search for processes with the string in the first
    command-line argument and execute the action specified in the second
    command-line argument."""
    if len(sys.argv) < 2:
        print("Arguments must be given to proceed", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 3:
        print("An action must be given to proceed", file=sys.stderr)
        sys.exit(2)

    if sys.argv[2] != "suspend" and sys.argv[2] != "continue":
        print(
            f"Unrecognized action: {sys.argv[2]}\n"
            "The action can be either 'suspend' or 'continue'",
            file=sys.stderr,
        )
        sys.exit(3)
    else:
        process_txt = sys.argv[1]
        suspend = "suspend" in sys.argv[2]

    our_pid = psutil.Process()
    pids = {
        ps.pid: ps
        for ps in psutil.process_iter()
        if process_txt in "".join(ps.cmdline())
    }
    if our_pid.pid in pids:
        del pids[our_pid.pid]

    if len(pids) < 1:
        print("No processes found", file=sys.stderr)
        sys.exit(4)

    for pid in pids.values():
        if suspend:
            pid.suspend()
        else:
            pid.resume()

    print(f"Signaled {len(pids)} process", end="")
    if len(pids) > 1:
        print("es")
    else:
        print()


if __name__ == "__main__":
    main()
