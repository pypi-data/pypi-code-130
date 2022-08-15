from typing import Optional, TextIO, Union

import click
import pkg_resources

from d3tree import html_template, node, utils


def read_file(filepath: str, node: node.Node):
    with open(file=filepath, mode="r") as f:
        lines = filter(None, (line.strip() for line in f))
        for line in lines:
            node.insert_node(path=line.split("/"))


@click.command()
@click.argument("path", type=click.Path(exists=True, file_okay=True, dir_okay=True), required=False)
@click.option("--version", "-v", is_flag=True, help="Print version")
@click.option("--output", "-o", required=False, help="Specify filepath to write HTML output")
@click.option(
    "--template",
    "-t",
    type=click.Choice(["tree", "circles", "flame", "treemap"]),
    default="tree",
    help="Specify template",
)
def main(
    path: Optional[Union[str, TextIO]], version: None, output: Optional[str], template: utils.AllowedTemplate
) -> None:
    if version:
        click.echo(pkg_resources.require("d3tree")[0].version)
        return None

    if path and isinstance(path, str):
        iter_ = utils.read_from_filepath(path=path)
    elif click.get_text_stream("stdin"):
        iter_ = utils.read_from_stdin()
    else:
        return None

    data = utils.create_node(iter_=iter_)
    content = html_template.process_html(data=data, template=template, output=output)
    if content is not None:
        click.echo(content)


if __name__ == "__main__":
    main()
