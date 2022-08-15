import pkgutil
from string import Template
from typing import Optional

from d3tree import node, utils


class HtmlTemplate(Template):
    delimiter = "{%"  # to be replaced in HTML template


def read_html_template(template: str) -> str:
    content = pkgutil.get_data(__name__, f"templates/{template}.html")
    return content.decode(encoding="UTF-8")  # type: ignore


def write_html_file(filepath: str, content: str) -> None:
    with open(file=f"{filepath}", mode="w") as target:
        target.write(content)


def process_html(data: node.Node, template: utils.AllowedTemplate, output: Optional[str] = None) -> Optional[str]:
    html_file = read_html_template(template=template)

    s = HtmlTemplate(html_file)
    content = s.substitute(data=data)

    if output:
        write_html_file(filepath=output, content=content)
        return None

    return content
