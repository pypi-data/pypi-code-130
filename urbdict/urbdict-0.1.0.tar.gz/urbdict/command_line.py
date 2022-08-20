import sys
from urbdict import main


def define():
    arg = " ".join(sys.argv[1:])
    result = main.define(arg)
    output = "{}\n\n  {} \n\nEx: {}\n\n {}\n\n{}".format(
        result["word"],
        result["definition"],
        result["example"],
        result["contributor"],
        result["url"],
    )
    print(output)
