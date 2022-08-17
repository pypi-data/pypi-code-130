import os
import argparse
import logging
import sys
from _version import __version__

_logger = logging.getLogger(__name__)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="visual-md: jupyter notebooks to visual reports.")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument(
        "--include-code",
        "--include-code",
        dest="include_code",
        action="store_const",
        const=True,
    )
    parser.add_argument(
        "-i",
        "--input-file",
        dest="input",
        help="provide input file",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        dest="output",
        help="provide output filename",
    )

    return parser.parse_args(args)


def get_codeCells(line_numbers, img_line_numbers, fname):
    """

    :param line_numbers:
    :param img_line_numbers: image line numbers
    :param fname: actual file name of input file
    :return: list of code cells with their associated code in the form:

                ```python

                >>> python code
                >>> more python code

                ```
    """

    code_cells = []

    for idx in range(len(line_numbers) - 1):

        code_cell = open(fname, "r").readlines()[line_numbers[idx]:line_numbers[idx + 1]]
        code_cell = ''.join(code_cell)

        for n in img_line_numbers:
            try:
                if (n > line_numbers[idx+1]) & (n < line_numbers[idx+2]):
                    code_cells.append(code_cell)
            except Exception:
                pass

    os.remove(fname)

    return code_cells


def insert_images(code_cells, image_calls, include_code: bool):
    """

    :param code_cells:
    :param image_calls:
    :param include_code: Whether to include code cells associated with the plots or not
                         defaults to True
    :return: a string document with all contents(plots and their associated code) that
             will be exported as markdown
    """

    document = """<h1 align="center">Plots</h1>\n\n-----\n\n"""

    if include_code:
        for code_cell, img_call in zip(code_cells, image_calls):

            # centered image
            img_call_centered = f"""\n<p align="center">\n\t<img src='{img_call.split(']')[-1].strip().strip(')').strip('(')}'/>\n</p>\n"""

            document += ('```python\n' + code_cell + "\n" + img_call_centered + "\n")
    else:
        for img_call in image_calls:
            img_call_centered = f"""\n<p align="center">\n\t<img src='{img_call.split(']')[-1].strip().strip(')').strip('(')}'/>\n</p>\n"""
            document += ("\n" + img_call_centered + "\n")

    return document


def get_code_img_lines(fname):
    """
    Get code and image line numbers
    :param fname: file name of notebook to convert
    :return:
    """

    line_numbers = []
    img_calls = []
    img_line_numbers = []

    for l_number, l in enumerate(open(fname, "r").readlines(), start=1):
        if l.startswith("```"):
            line_numbers.append(l_number)
        elif l.startswith("![png]"):
            img_calls.append(l)
            img_line_numbers.append(l_number)

    return line_numbers, img_calls, img_line_numbers


def main(args=None):

    if args is None:
        args = parse_args(args)

    setup_logging(logging.INFO)

    # convert jupyter notebook(ipynb) to markdown(md)
    input_file = args.input
    os.system(f"jupyter nbconvert {input_file} --to markdown")
    fname = f"{'.'.join(input_file.split('.')[:-1])}.md"

    line_numbers, img_calls, img_line_numbers = get_code_img_lines(fname)

    code_cells = get_codeCells(line_numbers, img_line_numbers, fname)

    document = insert_images(code_cells, image_calls=img_calls, include_code=args.include_code)

    # export document
    with open(args.output, "w") as out_file:
        out_file.write(document)
        out_file.close()

    _logger.info(f"saved output file as [{args.output}]")

if __name__ == "__main__":
    main(sys.argv[1:])