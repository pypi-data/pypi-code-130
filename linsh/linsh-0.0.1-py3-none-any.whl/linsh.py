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
        """ > """
        # return None, but directly print stdout and stderr
        if other is None:
            sp.run(self.init, shell=True, encoding="utf-8")
        # return (stderr + stdout), but not print
        elif other is Ellipsis:
            return sp.run(self.init, shell=True, encoding="utf-8", stderr=sp.PIPE, stdout=sp.PIPE)
        # # return stdout
        # elif other == 1:
        #     sp.run(self.init, shell=True, encoding="utf-8", stdout=sp.PIPE)
        # # return stderr
        # elif other == 2:
        #     sp.run(self.init, shell=True, encoding="utf-8", stderr=sp.PIPE, )

def main():
    cmd = "ls -al"
    c = LinSH(cmd)
    # -c

    cmd1 = "grep py"
    cmd2 = "grep 123"

    c | cmd1 | cmd2 > None          # return None, but directly print stdout and stderr

    result = c | cmd1 | cmd2 > ...  # return <subprocess obj> but not print
    print(result.stdout, result.stderr)

    # in the future ...
    # c | cmd1 | cmd2 > 1   # stdout
    # c | cmd1 | cmd2 > 2   # stderr

if __name__ == '__main__':
    main()