import requests
import typer
from codex_taps.decrypter import decrypt
from rich import print

app = typer.Typer()


@app.callback()
def main():
    """
    CODEx Final Package
    """


@app.command()
def get_input(number: int = typer.Argument(..., help="Puzzle number")):
    m_file = open(f"input_{number}.txt", "w")
    m_req = requests.get(f"https://codex-fn-in.netlify.app/{number}.txt").text
    m_file.write(m_req)
    m_file.close()


@app.command()
def check_answer(puzzle: int, answer: str):
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

    print(f"{'[green]' if is_correct else '[red]'}{answer} is the {'correct' if is_correct else 'incorrect'} answer to Puzzle {puzzle}!")


if __name__ == "__main__":
    app()
