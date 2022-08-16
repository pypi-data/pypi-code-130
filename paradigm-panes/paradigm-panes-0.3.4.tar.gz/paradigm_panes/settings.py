from pathlib import Path

# The order in which paradigm sizes will be presented to the user.
# The first size in this list is the "default".
# Make sure to exhaustively specify all size options available!
MORPHODICT_PARADIGM_SIZES = [
    # The most user-friendly size should be first:
    "basic",
    # Then, a more complete paradigm layout:
    "full",
    # Variants for linguists go here:
]

STRICT_GENERATOR_FST_FILEPATH = ""
STRICT_GENERATOR_FST_WITH_MORPHEMES_FILEPATH = ""
STRICT_ANALYSER_FST_FILEPATH = ""
LAYOUTS_DIR = ""
TAG_STYLE = "Plus"


class FileDoesNotMatch(Exception):
    """
    Raised when file cannot be found or does not match .hfstol extension
    """


def set_fst_filepath(filepath: str) -> None:
    """
    Set a path to FST file
    """
    if Path(filepath).is_file() and Path(filepath).match("*.hfstol"):
        global STRICT_GENERATOR_FST_FILEPATH
        STRICT_GENERATOR_FST_FILEPATH = filepath
    else:
        raise FileDoesNotMatch(f"file {Path(filepath).as_posix()!r} does not exist or does not end in \".hfstol\".")


def set_morpheme_fst_filepath(filepath: str) -> None:
    """
        Set a path to the morpheme generation FST file
        """
    if Path(filepath).is_file() and Path(filepath).match("*.hfstol"):
        global STRICT_GENERATOR_FST_WITH_MORPHEMES_FILEPATH
        STRICT_GENERATOR_FST_WITH_MORPHEMES_FILEPATH = filepath
    else:
        raise FileDoesNotMatch(f"file {Path(filepath).as_posix()!r} does not exist or does not end in \".hfstol\".")


def set_analyser_fst_filepath(filepath: str) -> None:
    """
        Set a path to the morpheme generation FST file
        """
    if Path(filepath).is_file() and Path(filepath).match("*.hfstol"):
        global STRICT_ANALYSER_FST_FILEPATH
        STRICT_ANALYSER_FST_FILEPATH = filepath
    else:
        raise FileDoesNotMatch(f"file {Path(filepath).as_posix()!r} does not exist or does not end in \".hfstol\".")


def get_fst_filepath() -> str:
    """
    Get a path to FST file
    """
    return STRICT_GENERATOR_FST_FILEPATH


class DirectoryDoesNotExist(Exception):
    """
    Raised when directory with paradigm layouts is missing
    """


def set_layouts_dir(dir_path: str) -> None:
    """
    Set a directory with paradigm layouts
    """
    if Path(dir_path).is_dir():
        global LAYOUTS_DIR
        LAYOUTS_DIR = dir_path
    else:
        raise DirectoryDoesNotExist(f"Directory {dir_path!r} does not exist.")


def get_layouts_dir() -> str:
    """
    Get a directory with paradigm layouts
    """
    return LAYOUTS_DIR


def is_setup_complete():
    """
    Confirms that both FST and Layouts folder are configured and valid.
    """
    return Path(LAYOUTS_DIR).is_dir() and (Path(STRICT_GENERATOR_FST_FILEPATH).is_file() and Path(STRICT_GENERATOR_FST_FILEPATH).match("*.hfstol"))


# In case all_analysis_template_tags() will be need to be called from panes package
def set_tag_style(tag_style: str) -> None:
    """
    Set tag style

    Available tags:
        1. "Plus"
        2. "Bracket"
    """
    global TAG_STYLE
    TAG_STYLE = tag_style


def get_tag_style() -> str:
    """
    Get tag style
    """
    return TAG_STYLE
