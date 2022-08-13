#!python

import getopt
import json
import sys

from DeTrusty.Molecule.MTCreation import DEFAULT_OUTPUT_PATH, create_rdfmts, logger


def get_options(argv):
    try:
        opts, args = getopt.getopt(argv, 'h:s:o:j')
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    endpoints_file = None
    output = DEFAULT_OUTPUT_PATH
    is_json = False
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt == '-s':
            endpoints_file = arg
        elif opt == '-o':
            output = arg
        elif opt == '-j':
            is_json = True

    if not endpoints_file:
        usage()
        sys.exit(1)

    if not is_json:
        with open(endpoints_file, 'r') as f:
            endpoints = f.readlines()
            if len(endpoints) == 0:
                logger.critical("The endpoints file should contain at least one URL")
                sys.exit(1)
            endpoints = [e.strip('\n') for e in endpoints]
    else:
        with open(endpoints_file, 'r') as f:
            endpoints = json.load(f)

    if '.json' not in output:
        output += '.json'
    return endpoints, output


def usage():
    usage_str = (
        'Usage: {program} -s <path/to/endpoints.txt> [-o <path/to/output.json>] [-j]\n'
        'where\n'
        '    <path/to/endpoints.txt> - path to a text file containing a list of SPARQL endpoint URLs\n'
        '    <path/to/output.json> - name of output file\n'
        'parameters\n'
        '    -j\tif set, the endpoints file will be handled as JSON instead of plain text'
    )
    print(usage_str.format(program=sys.argv[0]),)


if __name__ == '__main__':
    endpoints, output = get_options(sys.argv[1:])
    create_rdfmts(endpoints, output)
