import pytermgui as ptg

with ptg.terminal.record() as rec:
    with open("docs/src/source.py", "r") as f:
        hi = ptg.highlight_python(f.read())

    parsed = ptg.tim.parse(hi)
    print(repr(parsed))
    ptg.terminal.print(parsed)

rec.save_svg("out.svg")
