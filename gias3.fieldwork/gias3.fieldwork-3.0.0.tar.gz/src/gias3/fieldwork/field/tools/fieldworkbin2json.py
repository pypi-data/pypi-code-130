"""
Script to update binary fieldwork files to json text format
"""

import argparse
import logging
import os
import sys
from glob import glob

from gias3.fieldwork.field import ensemble_field_function as eff
from gias3.fieldwork.field import geometric_field as gf
from gias3.fieldwork.field.topology import mesh

log = logging.getLogger(__name__)


# =============================================================================#
def is_json(in_path):
    with open(in_path, 'r') as f:
        head = f.read(1)
        if head == '{':
            return True
        else:
            return False


def _make_out_path(in_path, keep_old):
    out_path = os.path.splitext(in_path)[0]
    if keep_old:
        out_path = out_path + '_json'
    return out_path


def convert_geof(in_path, out_path, keep_old, verbose=False):
    obj = gf.load_geometric_field(in_path, force=True)
    if out_path is None:
        out_path = _make_out_path(in_path, keep_old)

    if verbose:
        log.debug('output filename: {}'.format(out_path))
    obj.save_geometric_field(out_path)


def convert_ens(in_path, out_path, keep_old, verbose=False):
    obj = eff.load_ensemble(in_path, force=True)
    if out_path is None:
        out_path = _make_out_path(in_path, keep_old)

    if verbose:
        log.debug('output filename: {}'.format(out_path))
    obj.save_ensemble(out_path)


def convert_mesh(in_path, out_path, keep_old, verbose=False):
    obj = mesh.load_mesh(in_path)
    if out_path is None:
        out_path = _make_out_path(in_path, keep_old)

    if verbose:
        log.debug('output filename: {}'.format(out_path))
    obj.save_mesh(out_path)


converters = {
    '.geof': convert_geof,
    '.ens': convert_ens,
    '.mesh': convert_mesh,
}


def convert_file(in_path, out_path=None, keep_old=False, verbose=False):
    if verbose:
        log.debug('converting {}'.format(in_path))

    # check is not json already
    if is_json(in_path):
        if verbose:
            log.debug('Input file is already in json text format. Aborting.')
        return

    # identify file type
    ext = os.path.splitext(in_path)[1].lower()
    converter = converters.get(ext)
    if converter is None:
        raise ValueError('Unknown file extension {}'.format(ext))

    converter(in_path, out_path, keep_old, verbose=verbose)


def convert_dir(in_path, keep_old=False, verbose=False):
    # get all .geof files
    geof_files = glob(os.path.join(in_path, '*.geof'))
    if verbose:
        log.debug('Converting {} .geof files'.format(len(geof_files)))
    for gff in geof_files:
        convert_file(gff, keep_old=keep_old, verbose=verbose)

    # get all .ens files
    ens_files = glob(os.path.join(in_path, '*.ens'))
    if verbose:
        log.debug('Converting {} .ens files'.format(len(ens_files)))
    for enf in ens_files:
        convert_file(enf, keep_old=keep_old, verbose=verbose)

    # get all .ens files
    mesh_files = glob(os.path.join(in_path, '*.mesh'))
    if verbose:
        log.debug('Converting {} .mesh files'.format(len(mesh_files)))
    for mf in mesh_files:
        convert_file(mf, keep_old=keep_old, verbose=verbose)


# =============================================================================#
def make_parser():
    parser = argparse.ArgumentParser(
        description='Convert binary fieldwork files (.geof, .ens, .mesh) to json text format'
    )
    parser.add_argument(
        'in_path',
        help='Path to file or directory. If directory, all fieldwork files will be converted'
    )
    parser.add_argument(
        '-o', '--outfile',
        help='Output filename. Default is to overwrite original file. If in_path is a directory, this is ignored.'
    )

    parser.add_argument(
        '-k', '--keep_old',
        action='store_true',
        help='Keep old binary file. New file will be named with a _json suffix'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Extra info.'
    )
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    # =============================================================================#
    # check path is valid
    if not os.path.exists(args.in_path):
        raise ValueError('Invalid input path.')

    # check output path is valid
    if args.outfile is not None:
        out_dir = os.path.dirname(args.outfile)
        if not os.path.isdir(out_dir):
            raise ValueError('Invalid output file directory.')

    # check if in_path is a file or a directory
    if os.path.isdir(args.in_path):
        convert_dir(args.in_path, keep_old=args.keep_old, verbose=args.verbose)
    else:
        convert_file(args.in_path, out_path=args.outfile, keep_old=args.keep_old, verbose=args.verbose)


if __name__ == '__main__':
    try:
        main()
        exit(0)
    except Exception as e:
        log.exception('Unexpected exception', e)
        exit(99)
