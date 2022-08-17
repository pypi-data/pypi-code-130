#!python
from optparse import OptionParser
from os.path import exists

import mmf_setup

# List of (variable, value, filename)
# Will print a statement like the following iff filename is None or exists:
#
#    export variable=value
#
VARIABLES = [
    ("MMF_SETUP", mmf_setup.MMF_SETUP, mmf_setup.MMF_SETUP),
]


def get_HGRCPATH(full_hg=False):
    """Return the HGRCPATH.

    Arguments
    ---------
    full_hg : bool
       If True, then include the potentially dangerous HGRC_FULL file which includes the
       update hook.
    """
    paths = [mmf_setup.HGRC_FULL if full_hg else mmf_setup.HGRC_LGA]
    paths = [path for path in paths if exists(path)]
    paths.insert(0, "${HGRCPATH:-~/.hgrc}")
    return ":".join(paths)


def run(debug=False, full_hg=False):
    global VARIABLES
    vars = list(VARIABLES)
    vars.append(("HGRCPATH", get_HGRCPATH(full_hg=full_hg), None))
    env = []

    for var, value, filename in vars:
        if not filename or exists(filename):
            env.append('export {var}="{value}"'.format(var=var, value=value))
        elif debug:
            print(
                "# processing {}={} failed:\n   no file '{}'".format(
                    var, value, filename
                )
            )

    print("\n".join(env))


parser = OptionParser()
parser.add_option(
    "-d",
    "--debug",
    action="store_true",
    dest="debug",
    default=False,
    help="debug missing files",
)
parser.add_option(
    "-H",
    "--hg",
    action="store_true",
    dest="full_hg",
    default=False,
    help="""Include hgrc.full in HGRCPATH with a complete set of mercurial options
including: the evolve extension with topics enabled, the hggit extension so you can
clone from git, and an update hook to include project-specific .hgrc file to .hg/hgrc.
(Note: this is a POTENTIAL SECURITY RISK.  Make sure you inspect the .hgrc file
before running further mercurial commands.)""",
)

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    run(debug=options.debug, full_hg=options.full_hg)
