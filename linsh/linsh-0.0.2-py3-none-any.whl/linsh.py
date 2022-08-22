import subprocess as sp


class LinSH(str):
    def __init__(self, init: str):
        self.init = init

    def __or__(self, command: str):
        """ | """
        self.init = f"{self.init} | {command}"
        return self

    def __neg__(self):
        """ - """
        sp.run(self.init, shell=True)

    def __gt__(self, other):
        sub_obj = sp.run(self.init, shell=True, encoding="utf-8", stderr=sp.PIPE, stdout=sp.PIPE)

        """ > """
        # return None, but directly print stdout and stderr
        if other is None:
            sp.run(self.init, shell=True, encoding="utf-8")
        # return (stderr + stdout), but not print
        elif other is Ellipsis:
            return sub_obj
        # # only return stdout, not print
        elif other == 1:
            return sub_obj.stdout
        # # only return stderr, not print
        elif other == 2:
            return sub_obj.stderr
