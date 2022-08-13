import os
import platform

class settings:
    force_colours = False

class __config:
    escape_start = "\033[0;"
    escape_end = "m"

    colour_prefix = {
        "foreground": 3,
        "background": 4
    }

    colour_suffix = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
        "none": 9,
    }

    style_prefix = {
        "none": 0,
        "bright": 1,
        "dim": 2,
        "italic": 3,
        "underline": 4,
        "slow blink": 5, 
        "fast blink": 6,
        "invert": 7,
        "hide": 8,
        "strikethrough": 9,
        "double underline": 21,
        "overline": 53,
    }

def colour(text:str, foreground:str = "none", background:str = "none"):
    if ("TERM" not in os.environ.keys() or platform.uname().system == "Windows") and not settings.force_colours:
        return text

    if foreground not in __config.colour_suffix:
        raise TypeError(f"\"{foreground}\" is not a valid colour")

    if background not in __config.colour_suffix:
        raise TypeError(f"\"{background}\" is not a valid colour")

    prefix = f"{__config.escape_start}3{__config.colour_suffix[foreground]};4{__config.colour_suffix[background]}{__config.escape_end}"
    suffix = f"{__config.escape_start}39;49{__config.escape_end}"
    return f"{prefix}{text}{suffix}"

def style(text:str, style:str = "none"):
    if ("TERM" not in os.environ.keys() or (platform.uname().system == "Windows" and "TERM" not in os.environ.keys())) and not settings.force_colours:
        return text

    if style not in __config.style_prefix:
        raise TypeError(f"\"{style}\" is not a valid style")

    prefix = f"{__config.escape_start}{__config.style_prefix[style]}{__config.escape_end}"
    suffix = suffix = f"{__config.escape_start}0{__config.escape_end}"
    return f"{prefix}{text}{suffix}"

def help():
    print("Foreground Colours")
    for _colour in __config.colour_suffix:
        print("  \u21B3", f"\"{_colour}\"", "foreground: ", colour(_colour, foreground = _colour))

    print("Background Colours")
    for _colour in __config.colour_suffix:
        print("  \u21B3", f"\"{_colour}\"", "background: ", colour(_colour, background = _colour))

    print("Styles")
    for _style in __config.style_prefix:
        print("  \u21B3", f"\"{_style}\"", "style: ", style(_style, _style))