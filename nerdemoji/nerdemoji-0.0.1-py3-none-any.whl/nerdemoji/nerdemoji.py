def nerdemojirun(code):
    try:
        code()
    except Exception as e:
        print(e)
        print(f'"{e}"\n-🤓')
