#!/usr/bin/env python3

import datetime
import sys

from vkostyanetsky import cliutils

from fastimer import datafile, statistics, utils
from fastimer.browser import FastsBrowser
from fastimer.menu import FastimerMenu


def main() -> None:
    """
    Main entry point of the application. Displays the main menu by default.
    """

    main_menu()


def main_menu():

    fasts = datafile.read_fasts()
    active_fast = utils.get_active_fast(fasts)

    menu = FastimerMenu(active_fast)

    if active_fast is None:
        menu.add_item("Start New Fast", start_fast)
    else:
        menu.add_item("Stop Active Fast", stop_fast)

    menu.add_item("Fasts Browser", show_fasts_browser)
    menu.add_item("Statistics", show_statistics)
    menu.add_item("Exit", sys.exit)

    menu.choose()


def start_fast() -> None:
    fasts = datafile.read_fasts()
    fast = utils.get_active_fast(fasts)

    if fast is not None:

        print("Fast is already on.")
        print()

        cliutils.enter_to_continue()

    else:

        length = None

        while length is None:

            user_input = input("Enter fast duration in hours: ")

            if user_input.isdigit():

                length = int(user_input)
                fast = {
                    "length": length,
                    "started": datetime.datetime.now(),
                }

                fasts.append(fast)

                datafile.write_fasts(fasts)

            else:

                print("Please enter a valid number.")
                print()

        main_menu()


def stop_fast() -> None:

    fasts = datafile.read_fasts()
    active_fast = utils.get_active_fast(fasts)

    menu = FastimerMenu(active_fast)

    menu.add_item("Finish Fast", finish_fast)
    menu.add_item("Cancel Fast", cancel_fast)
    menu.add_item("Back", main_menu)

    menu.choose()


def cancel_fast() -> None:
    """
    Cancel Fast
    """
    fasts = datafile.read_fasts()
    active_fast = utils.get_active_fast(fasts)

    cliutils.clear_terminal()

    prompt = "Do you want to CANCEL the active fast? It cannot be undone."

    if cliutils.prompt_for_yes_or_no(prompt):

        fasts.remove(active_fast)
        datafile.write_fasts(fasts)

    main_menu()


def finish_fast() -> None:
    """
    Finish Fast
    """
    fasts = datafile.read_fasts()

    cliutils.clear_terminal()

    if cliutils.prompt_for_yes_or_no("Do you want to end your ongoing fast?"):

        fasts[-1]["stopped"] = datetime.datetime.now()
        datafile.write_fasts(fasts)

    main_menu()


def show_fasts_browser() -> None:
    fasts = datafile.read_fasts()
    FastsBrowser(fasts).open()

    main_menu()


def show_statistics() -> None:

    fasts = datafile.read_fasts()

    print("FASTING STATISTICS")
    print()

    statistics.print_completed_fasts(fasts)
    statistics.print_total_fasting_time(fasts)
    statistics.print_average_fast_length(fasts)
    statistics.print_longest_fast_length(fasts)
    statistics.print_longest_fasting_streak(fasts)
    statistics.print_current_fasting_streak(fasts)
    print()

    statistics.print_achievements(fasts)
    print()

    cliutils.enter_to_continue()

    main_menu()
