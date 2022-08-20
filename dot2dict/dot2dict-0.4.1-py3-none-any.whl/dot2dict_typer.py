import rich
import typer

import re
import json
from enum import Enum

from rich.syntax import Syntax

from typing import Optional
from rich.panel import Panel

from rich.console import Console
from rich.markdown import Markdown


from dot2dict.docs import get_expanded_example

err_console = Console(stderr=True)

__version__ = "0.2.1"


# Misc Methods

class Language(str, Enum):
    none = "none"
    ruby = "ruby"
    python = "python"


def version_callback(value: bool):
    if value:
        print(f"Awesome CLI Version: {__version__}")
        raise typer.Exit()


def about_callback(value: bool):
    if value:
        print(f"Awesome CLI Version: {__version__}")
        print(f"About 🐕")
        raise typer.Exit()


def example_callback(value: bool):
    if value:
        markdown_string = get_expanded_example()
        console = Console()
        md = Markdown(markdown_string)
        console.print(md)
        print("\n")

        raise typer.Exit()


def complete_prefix():
    return [""]


def complete_suffix():
    return [""]


def complete_dict():
    return [""]


def main(
        dotnotation: str = typer.Argument(
            ...,
            help="JSON Dot notation string",
            metavar="dotnotation",
            rich_help_panel="Arguments",
        ),
        ruby: bool = typer.Option(
            False,
            "--ruby",
            "-r",
            help="Convert JSON Dot Notation to Ruby Hash Notation",
        ),
        python: bool = typer.Option(
            True,
            "--python",
            "-py",
            help="Convert JSON Dot Notation to Python Dictionary Notation",
        ),
        double_quotes: bool = typer.Option(
            False,
            "--double-quotes",
            "-dq",
            help="Uses Double Quotes to denote String Keys",
        ),
        dict_name: str = typer.Option(
            "",
            "--dict",
            "-d",
            help="Python Dictionary / Ruby Hash name",
            autocompletion=complete_dict,
        ),
        prefix: str = typer.Option(
            "",
            "--prefix",
            "-p",
            help="dot seperated prefix to be added before the input",
            autocompletion=complete_prefix,
        ),
        suffix: str = typer.Option(
            "",
            "--suffix",
            "-s",
            help="dot seperated suffix to be added after the input",
            autocompletion=complete_suffix,
        ),
        lang: Language = typer.Option(
            Language.python,
            "--lang",
            "-l",
            case_sensitive=False,
            help="Selects which programming language to convert to. \n Setting this will override all other options",
        ),
        max_array_size: int = typer.Option(
            1000,
            "--max-array-size",
            "-m",
            min=1,
            max=10000000,
            clamp=True,
            help="Maximum number of JSON Array length to consider before assuming it as JSON Key",
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Print Info as the program executes. Useful for debugging.",
        ),
        version: Optional[bool] = typer.Option(
            None,
            "--version",
            callback=version_callback,
            is_eager=True,
            rich_help_panel="Others",
            help="Print an awsome Version Info"
        ),
        about: Optional[bool] = typer.Option(
            None,
            "--about",
            callback=about_callback,
            is_eager=True,
            rich_help_panel="Others",
            help="Print an awsome about Info"
        ),
        example: Optional[bool] = typer.Option(
            None,
            "--example",
            callback=example_callback,
            is_eager=True,
            rich_help_panel="Others",
            help="Print an awsome Example"
        ),
):
    """
    Dot Notation to Dictionary and Hash Notation for Python 🐍 and Ruby ♦️.
    Provide JSON dot notation as input and get dictionary / hash notation as output.
    
    dot2dict on pypi : Visit https://pypi.org
    """

    config = {
        "dotnotation": dotnotation,
        "python": python,
        "ruby": ruby,
        "language": lang.value,
        "output_lang": "",
        "prefix": prefix,
        "suffix": suffix,
        "dict_name": dict_name,
        "max_json_array_size": max_array_size,
        "use_double_quotes": double_quotes,
        "filter_list": [None, "''"],
        "verbose": verbose,
        "version": version,
        "about": about,
        "example": example,
    }

    output_language = get_language_based_on_config(config)
    config['output_lang'] = output_language

    appearance_config = get_appearance_based_on_config(config)
    config['appearance'] = appearance_config

    validation = validate(config)

    if verbose:
        rich.print_json(json.dumps(config))
        if validation:
            print("The Options are Valid")
        else:
            print("The Options are not Valid. Please check them once.")

    result_string = convert_to_specified_format(dotnotation, config)

    pretty_print_text(result_string, config)


def generate_dot_2_dict(dot_string: str, config: dict) -> list[str]:
    """
    Function that take JSON dot notation as input and generate Dict / Hash notation as output.
    :param config:
    :param dot_string:
    :return:
    """
    final_literal = []
    digits_pattern = "\[(\d+)\]"
    max_json_array_size = config["max_json_array_size"]
    use_double_quotes = config["use_double_quotes"]
    filter_list = config["filter_list"]

    literal_list = dot_string.split(".")

    for literal in literal_list:

        if "[" in literal or "]" in literal:

            clean_literal = re.sub(digits_pattern, "", literal)
            final_literal.append(f"'{clean_literal}'")

            match_all_digits = re.findall(digits_pattern, literal)

            for digit in match_all_digits:
                value = None
                try:
                    value = int(digit.strip())
                except Exception as e:
                    print(f"Could not convert {digit} to Integer : {repr(e)}")

                if value is None:
                    print("It should not reach here. 😔")
                elif value < 0:
                    final_literal.append(f"'{value}'")  # Considering as JSON Key Value (with quotes)
                elif value < max_json_array_size:
                    final_literal.append(f"{value}")  # Considering as JSON Array Value (without quotes)
                else:
                    final_literal.append(f"'{value}'")  # Considering as JSON Key Value (with quotes)

        else:
            final_literal.append(f"'{literal}'")

    compact_literals = [val.strip() for val in final_literal if val.strip()]
    selected_literals = [val for val in compact_literals if val not in filter_list]

    if use_double_quotes:
        result_list = [re.sub("'", '"', element) for element in selected_literals]
    else:
        result_list = selected_literals

    return result_list


def validate(config: dict) -> bool:
    # Checking if both Python and Ruby are chosen.
    is_valid = False
    if config['python'] and config['ruby']:
        print(f"You have set Python as {config['python']} and Ruby as {config['ruby']}")
        is_valid = False
    else:
        is_valid = True

    return is_valid


def get_language_based_on_config(config: dict) -> str:
    language = "python"
    if config['language'] == "python":
        language = "python"
    elif config['language'] == "ruby":
        language = "ruby"
    elif config['python']:
        language = "python"
    elif config['ruby']:
        language = "ruby"
    else:
        print("Invalid Options")

    return language


def get_appearance_based_on_config(config: dict) -> dict:
    appearance_config = {
        "panel_color": "green",
        "panel_heading": " Code ",
        "panel_subtitle": " Copy from Below Snippet "
    }

    if config['output_lang'] == "python":
        appearance_config['panel_color'] = "yellow"
        appearance_config['panel_heading'] = " Python 🐍 Dictionary "
        appearance_config['panel_subtitle'] = " Copy from Below Snippet "
    elif config['output_lang'] == "ruby":
        appearance_config['panel_color'] = "red"
        appearance_config['panel_heading'] = " Ruby ♦ Hash "
        appearance_config['panel_subtitle'] = " Copy from Below Snippet "
    else:
        print("Code should not reach here")

    return appearance_config


def convert_to_specified_format(text: str, config: dict) -> str:
    result_string = None

    prefix_list = []
    suffix_list = []
    if config['prefix']:
        prefix_list = generate_dot_2_dict(config['prefix'], config)

    if config['suffix']:
        suffix_list = generate_dot_2_dict(config['suffix'], config)

    result_list = generate_dot_2_dict(text, config)

    final_list = prefix_list + result_list + suffix_list

    if config['output_lang'] == "python":
        result_string = format_to_python(final_list, config)
    elif config['output_lang'] == "ruby":
        result_string = format_to_ruby(final_list, config)
    else:
        print("Hmm. The Code should not reach here. Please file a bug report.")

    return result_string


def format_string(text: str, config: dict) -> str:
    pass


def format_to_ruby(final_list: list, config: dict) -> str:
    result = f"{config['dict_name']}.dig({', '.join(final_list)})"
    return result


def format_to_python(final_list: list, config: dict) -> str:
    result_list = [f"[{val}]" for val in final_list]
    result = f"{config['dict_name']}{''.join(result_list)}"
    return result


def pretty_print_text(text: str, config: dict) -> None:
    print("\n")

    console = Console()
    syntax_text = Syntax(
        text,
        config['output_lang'],
        word_wrap=True,
        background_color="default"
    )
    rich.print(
        Panel(
            syntax_text,
            title_align="center",
            padding=(1, 5),
            safe_box=True,
            style=config['appearance']['panel_color'],
            title=config['appearance']['panel_heading'],
            subtitle=config['appearance']['panel_subtitle'],
            highlight=True,
            expand=False,
        )
    )
    print(f"\n\t{text}\n\n")


def start() -> None:
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
