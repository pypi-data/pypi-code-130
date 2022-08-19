import requests
import typer
from rich import print

from codex_taps.decrypter import decrypt

app = typer.Typer()


@app.callback()
def main():
    """
    CODEx Final Utility Tool
    """


@app.command()
def get_input(puzzle: str = typer.Argument(..., help="Puzzle number")) -> bool:
    """To get the input for the specific puzzle or all puzzles

    Args:
        puzzle (str, optional): Puzzle number. Defaults to typer.Argument(..., help="Puzzle number").

    Raises:
        ValueError: Error if the puzzle number is not valid.

    Returns:
        bool: If it worked or not.
    """
    try:
        if puzzle == "all":
            get_all_inputs()
            return
        m_file = open(f"input_{puzzle}.txt", "w")
        m_req = requests.get(
            f"https://codex-fn-in.netlify.app/{puzzle}.txt")
        if m_req.status_code != 200:
            raise ValueError("Invalid puzzle number")
        m_file.write(m_req.text)
        m_file.close()
        return True
    except Exception as e:
        print("[red]There was an error processing your request.")
        return False


def get_all_inputs():
    for i in range(1, 6):
        m_file = open(f"input_{i}.txt", "w")
        m_req = requests.get(f"https://codex-fn-in.netlify.app/{i}.txt").text
        m_file.write(m_req)


@app.command()
def check_answer(puzzle: int, answer: str) -> bool:
    """A function to check all the answers for the puzzles at CODEx

    Args:
        puzzle (int): Puzzle number.
        answer (str): Answer to the puzzle.

    Raises:
        ValueError: Error if the puzzle number is not valid.

    Returns:
        bool: If it worked or not.
    """
    try:
        is_correct = False
        if puzzle == 1:
            if answer == decrypt("gAAAAABi_6vu95gAmcQwaioGp7Jad7GK0lenWaBwQnqyZDzecNTID9cYt7_f6Pubwr2GKoi_u2zNuvGQU2i92RYtP8VrTbWckQ=="):
                is_correct = True
        elif puzzle == 2:
            if answer == decrypt("gAAAAABi_65c2iQ67UmxdDkW4IrMHyLdLInhXal5uusyxGW8vaX_XHprmOXNzPSnjqjuUaKkT7YDdTCWXwf3zya9nza8rK1Aiw=="):
                is_correct = True
        elif puzzle == 3:
            if answer == decrypt("gAAAAABi_7AVRdQCM6mSal-Zko7xfiK9QaS15tt1mnavDki6bdhUZ7vXj8ibXk02HwPnF1JqoLTwH0SOksI-_Iw7fKUJLNDbHQ=="):
                is_correct = True
        elif puzzle == 4:
            if answer == decrypt("gAAAAABi_7EXL6lNrqYLCsYcYIlR7rxIkWjINHkmEgE3zR7AF6rgIqquQMLEq8se6B0Ib1TX0LFuQlZlWTvgM9QKtqpp_fmIqQ=="):
                is_correct = True
        elif puzzle == 5:
            if answer == decrypt("gAAAAABi_7GaWnwERN3fHrV61lMeHR8QKAedmGBJe3SnexZ5PiIEurk2dEWdJo00zeKsrT5qUGI7yhCt-FBvFFOwL2hn4FZMcM_YMap-hDmGrlV_P6h46mc="):
                is_correct = True
        else:
            raise ValueError("Invalid puzzle number")

        print(f"{'[green]' if is_correct else '[red]'}{answer} is the {'correct' if is_correct else 'incorrect'} answer to Puzzle {puzzle}!")
        return True
    except Exception as e:
        print("[red]There was an error processing your request.")
        return False


if __name__ == "__main__":
    app()
