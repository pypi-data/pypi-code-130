import os

cli_call_dirpath = None


class SVGLocator(object):
    """
    this class assists in tracking down svg files referenced in pages yml files
    """

    def __init__(self, svg_path, pages_path):
        """accepts a path that may be relative to one or more configurable paths"""
        self.svg_path = svg_path
        self.abs_pages_path = os.path.realpath(pages_path)

        if not os.path.exists(self.abs_pages_path):
            raise FileNotFoundError(pages_path)

    @classmethod
    def set_call_dirpath(cls, dirpath=None):
        """
        store a frame of reference dir for use in resoving relative dirpaths
        """
        global cli_call_dirpath
        cli_call_dirpath = dirpath or os.getcwd()

    @staticmethod
    def call_dirpath():
        """
        return the dirpath registered as the current working directory
        when the script was called
        """
        return cli_call_dirpath

    def filepath(self):
        """
        returns the absolute filepath to the svg that is confirmed to exist
        """
        # return the svg path if it's an absolute path and it exists
        if os.path.isabs(self.svg_path):
            if os.path.exists(self.svg_path):
                return self.svg_path
            else:
                raise(FileNotFoundError(f'{self.svg_path} does not exist'))

        # return the absolute path made by joining the dir containing the page def and the relative
        # svg path, if a file exists at the path
        abs_path_via_pages_def = os.path.join(os.path.dirname(self.abs_pages_path), self.svg_path)
        if os.path.exists(abs_path_via_pages_def):
            return abs_path_via_pages_def

        # return the absolute path made by joining the call dir and the relative
        # svg path, if a file exists at the path
        call_dirpath = self.call_dirpath()
        if call_dirpath:
            abs_path_via_call_dir = os.path.join(str(call_dirpath), self.svg_path)
            if os.path.exists(abs_path_via_call_dir):
                return abs_path_via_call_dir

        raise (FileNotFoundError(f'{self.svg_path} does not exist'))