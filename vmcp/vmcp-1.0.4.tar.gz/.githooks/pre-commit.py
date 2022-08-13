#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pre commit hook for git."""

import sys
from typing import TextIO
from subprocess import run  # nosec B404
from pylint.lint import Run as Pylint


def color(score: float) -> str:  # pylint: disable=redefined-outer-name
    """Return color based on given score.

    Args:
        score (float):
            Score.

    Returns:
        str:
            Color.

    """
    if score >= 7:
        return "green"
    elif score >= 3:
        return "yellow"
    else:
        return "red"


# Run Pylint and get score
default_stdout = sys.stdout
sys.stdout = type("Dummy", (TextIO,), {"write": lambda self, data: ()})()
score = round(Pylint(["./src"], exit=False).linter.stats.global_note, 1)
sys.stdout = default_stdout

# Update README file
FILENAME = "README.md"
content = ""  # pylint: disable=invalid-name
with open(FILENAME, "r+", encoding="utf-8") as file:
    for count, line in enumerate(file):
        if count == 3:
            content += (
                f"[![Pylint: {score}/10]"
                f"(https://img.shields.io/badge/"
                f"Pylint-{score}/10-{color(score)}.svg)]"
                f"(https://pylint.pycqa.org)\n"
            )
        else:
            content += line
    file.seek(0)
    file.truncate()
    file.write(content)

# Add updated README file to the stage
run(("git", "add", FILENAME), check=True)  # nosec B603
