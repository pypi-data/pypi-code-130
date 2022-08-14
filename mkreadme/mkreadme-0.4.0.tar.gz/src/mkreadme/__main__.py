from pathlib import Path

import click
import inquirer

from mkreadme.template import SectionTemplate, load_templates


def _generate_section(t: SectionTemplate) -> str:
    return f"## {t.icon if t.icon is not None else ''} {t.name}\n\n{t.markdown}\n"


@click.command()
@click.option(
    "--filename",
    type=click.Path(writable=True, dir_okay=False, path_type=Path),
    default="README.md",
)
def main(filename: Path) -> None:
    """Interactively generate a README.md file.

    Args:
        filename: The filename to write to.

    Example:
        $ mkreadme --filename README.md
    """
    # inquire title
    title = inquirer.text(message="Input readme title")

    # inquire sections
    templates = load_templates()
    selected_slugs = inquirer.checkbox(
        message="Select sections to include",
        choices=[t.slug for t in templates],
        carousel=True,
    )

    # generate markdown
    selected_templates = filter(lambda t: t.slug in selected_slugs, templates)
    generated_sections = "\n".join(map(_generate_section, selected_templates))
    generated_readme = f"# {title}\n\n{generated_sections}"

    # write generated markdown to file
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(generated_readme)


if __name__ == "__main__":
    main()
