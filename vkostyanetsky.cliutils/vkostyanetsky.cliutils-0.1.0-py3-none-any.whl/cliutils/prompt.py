import platform
import subprocess


def clear_terminal():
    """
    Clear the terminal.
    """

    if platform.system().lower() == "windows":
        subprocess.check_call("cls", shell=True)
    else:
        print(subprocess.check_output("clear").decode())


def enter_to_continue(message: str = None) -> None:
    """
    A console prompt to ask the user to 'Press [Enter] to continue'.

    Args:
        message (str, optional): A message to display in place of the default.
    """
    if message:
        message = f"{message.rstrip()} "
    else:
        message = "Press [Enter] to continue "

    input(message)


def prompt_for_yes_or_no(prompt: str) -> bool:
    """
    Prompts the user with the specified question, and expects a yes or no response.
    Returns a boolean value representing the user's answer.

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        bool: True for yes, False for no.
    """
    prompt = f"{prompt} (y/n) "
    answer = input(prompt)

    return answer.strip().lower() == "y"
