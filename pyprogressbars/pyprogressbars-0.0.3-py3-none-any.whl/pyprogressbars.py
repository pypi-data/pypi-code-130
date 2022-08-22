import sys
import time


def colorize(color, text):
    """
    Colorize the given string with the given color
    Args:
         color(str): Color name. Supported values are green, yellow, red, blue, white
         text(str): Text which needs to be colorized
     Returns:
         colorized(str): Contains the colorized string
    """
    if color == "yellow":
        colorized = "\033[93m{}\033[0m".format(text)
    elif color == "red":
        colorized = "\033[91m{}\033[0m".format(text)
    elif color == "green":
        colorized = "\033[92m{}\033[0m".format(text)
    else:
        colorized = "\033[97m{}\033[0m".format(text)
    return colorized


def x_slash_y(prefix, x, y, show_percentage=False, color="white"):
    """
    Use it when you want to indicate the current progress out of total items. For example, 10 out 20 videos uploaded.
    It will be displayed as x/y on the CLI that is 10/20
    Args:
        prefix(str): Any prefix which you want to display before the
        x(int): indicates the current progress out of the required total value
        y(int): indicates the count of the max value
        show_percentage(bool): If true then the progress percentage will also be shown
        color(str): Color of the progress indicator
    Returns: None
    """
    percentage = round((x/y)*100, 2)
    if not show_percentage:
        sys.stdout.write(colorize(color, f"\r{prefix}{x}/{y}"))
    else:
        sys.stdout.write(colorize(color, f"\r{prefix}{x}/{y} ({percentage} %)"))
    sys.stdout.flush()


def growing_progress_bar(length, interval, prefix="", color="white"):
    """
    Shows the given text in a blinking effect
    Args:
        prefix(str): Any prefix which you want to display before the
        length(int): Length of the progress bar
        interval(float): Interval at which the progress bar should grow
        color(str): Color of the progress indicator
    Returns:
        None
    """
    for _ in range(length):
        if _ == 0:
            continue
        else:
            sys.stdout.write(colorize(color, "\r{0}{1}>".format(prefix, "="*_)))
        sys.stdout.flush()
        time.sleep(interval)


def filling_progress_bar(width, current_progress,delay=0.1, prefix="",color="white", show_percentage=False):
    """
    Creates a self filling progress bar in which the progress keeps filling based on the value of current_progress param
    Args:
        current_progress(int): Current progress value
        width(int): The width of the progress bar
        color(str): Color of the progress indicator
        prefix(str): Prefix to be displayed before the progress bar
        delay(float): Delay between the progress bar increase
        show_percentage(bool): If true then the progress percentage will also be shown
    Returns:
        None
    """
    progress_x, progress_y = "",""
    for i in range(width):
        if i < current_progress:
            progress_x += colorize(color, "|")
        else:
            progress_y += colorize("white", "|")
    if show_percentage:
        percentage = colorize(color, str(round((current_progress/width)*100, 2))+"%")
        sys.stdout.write(f"\r{prefix}{progress_x}{progress_y} {percentage}")
    else:
        sys.stdout.write(f"\r{prefix}{progress_x}{progress_y}")
    sys.stdout.flush()
    time.sleep(delay)


def loading_spinner(prefix, color):
    """
    Displays a very simple loading spinner
    Args:
        prefix(str): Prefix to be used while displaying the spinner
        color(str): Color of the spinner
    """
    sys.stdout.write(colorize(color, f"\r{prefix}-"))
    sys.stdout.flush()
    time.sleep(0.25)
    sys.stdout.write(colorize(color, f"\r{prefix}\\"))
    sys.stdout.flush()
    time.sleep(0.25)
    sys.stdout.write(colorize(color, f"\r{prefix}|"))
    sys.stdout.flush()
    time.sleep(0.25)
    sys.stdout.write(colorize(color, f"\r{prefix}/"))
    sys.stdout.flush()
    time.sleep(0.25)


def counter(limit, prefix, delay, reverse=False):
    """
    Creates a counter that ends at the given limit
    Args:
        limit(int): Limit for the counter
        prefix(str): Prefix for the counter
        delay(float): Delay between the counter increments
        reverse(bool): If true then the counter starts from the given limit and goes till zero
    """
    if not reverse:
        for i in range(1, limit+1):
            sys.stdout.write(f"\r{prefix}{i}")
            sys.stdout.flush()
            time.sleep(delay)
    else:
        for i in range(limit, 0, -1):
            sys.stdout.write(f"\r{prefix}{i}")
            sys.stdout.flush()
            time.sleep(delay)
