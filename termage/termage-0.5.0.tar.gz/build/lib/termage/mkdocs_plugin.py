from dataclasses import dataclass, fields

from mkdocs.plugins import BasePlugin

from .execution import patched_sdtout_recorder, execute, set_colors

RE_BLOCK = re.compile(r"([^\n]*)\`\`\`termage(-svg)?(.*?)\n([\s\S]*?)\`\`\`")

OUTPUT_BLOCK_TEMPLATE = """
=== "{code_tab_name}"

    ```py
{code}
    ```

=== "{svg_tab_name}"
{svg}{{ align=center }}
"""

OUTPUT_SVG_TEMPLATE = "{indent}![{alt}]({path}){{ align=center }}"

DEFAULT_OPTS = {
    "width": 80,
    "height": 20,
    "tabs": ("Python", "Output"),
    "foreground": "#dddddd",
    "background": "#212121",
    "title": "",
    "include": None,
}


@dataclass
class TermageOptions:
    title: str = ""
    width: int = 80
    height: int = 24
    include: str = None
    foreground: str = "#dddddd"
    background: str = "#212121"
    tabs: tuple[str, str] = ("Python", "Output")


VALID_FIELDS = fields(TermageOptions)


class TermagePlugin(BasePlugin):
    def __init__(self) -> None:
        self._svg_count = 0

    def _get_next_path(self) -> str:
        """Gets the next SVG path."""

        self._svg_count += 1

        return f"assets/termage_{self._svg_count}.svg"

    def _parse_opts(self, options: str) -> TermageOptions:
        opt_dict = {}

        for option in re.split(r"(?<!\\) ", options):
            if len(option) == 0:
                continue

            try:
                key, value = option.split("=")
            except ValueError as error:
                raise ValueError(f"Invalid key=value pair {option!r}.") from error

            value = value.replace("\\", "")

            if key not in VALID_FIELDS:
                raise ValueError(
                    f"Unexpected key {key!r}. Please choose from {list(opt_dict)!r}."
                )

            if value.isdigit():
                value = int(value)

            elif isinstance(opt_dict[key], tuple):
                value = tuple(value.split(","))

            opt_dict[key] = value

        return TermageOptions(**opt_dict)

    def _replace_codeblock(self, matchobj) -> str:
        """Replaces a codeblock with the Termage content."""

        indent, svg_only, options, code = matchobj.groups()

        opts = self._parse_opts(options)

        code_formatted = ""
        for line in code.splitlines():
            line = line[len(indent) :]

            if line.startswith("&"):
                line = line.replace("&", "", 1)
            else:
                code_filtered.append(line)

            # if line == "":
            #     continue

            code_formatted += line + "\n"

        with patched_stdout_recorder(opts.width, opts.height) as recorder:
            execute(module=None, include=opts.include, code=code_formatted)

        path = self._get_next_path()
        recorder.save_svg(path, title=opts.title)

        code_indent = (len(indent) + 4) * " "

        if svg_only:
            return OUTPUT_SVG_TEMPLATE.format(indent=indent, alt=title, path=path)

        # Re-indent template to match original indentation
        template = ""
        for line in OUTPUT_BLOCK_TEMPLATE.splitlines():
            if line not in ("{code}", "{svg}{{ align=center }}"):
                line = indent + line

            template += line + "\n"

        code_tab, svg_tab = opts.tabs
        code_indented = "\n".join(code_indent + line for line in code_filtered)

        return template.format(
            svg=f"{code_indent}![]({path})",
            code_tab_name=code_tab,
            svg_tab_name=svg_tab,
            code=code_indented,
        )

    def on_page_markdown(self, markdown, page, files, config) -> str:
        """Replaces the termage markdown syntax."""

        return RE_BLOCK.sub(self._replace_codeblock, markdown)
