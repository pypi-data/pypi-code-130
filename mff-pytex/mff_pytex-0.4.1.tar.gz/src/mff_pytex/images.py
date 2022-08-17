"""Utilities for using images, graphs etc. in text."""


from typing import Optional
from mff_pytex.utils import Environment, command
from mff_pytex.packages import add_package, Package


class Picture(Environment):
    """Picture environment for including pictures, graphs etc.
    """
    def __init__(self, picture_path: str, *params: str, caption: Optional[str] = None, label: Optional[str] = None, settings: Optional[list] = None) -> None:
        """Initialize picture

        Args:
            picture_path (str): Path to picture.
            *params (str): Settings of figure.
            caption (str | None, optional): Caption of picture. Defaults to None.
            label (str | None, optional): Label of picture. Defaults to None.
            settings (str | None, optional): settings for picture eg. width. Defaults to None.
        """
        add_package(Package('graphicx'))
        self.en_type = 'figure'
        if params:
            self.write(command('begin', self.en_type, *params))
        else:
            self.write(command('begin', self.en_type))
        self.picture_path = picture_path
        self.caption = caption
        self.label = label
        self.settings = settings

    def __str__(self) -> str:
        """Returns content string encapsuled by picture environment.

        Returns:
            str: Content.
        """
        if self.settings:
            self.write(command('includegraphics', self.picture_path, *self.settings))
        else:
            self.write(command('includegraphics', self.picture_path))
        if self.label is not None:
            self.write(command('label', self.label))
        if self.caption is not None:
            self.write(command('caption', self.caption))
        return self._text + command('end', self.en_type) + '\n'
