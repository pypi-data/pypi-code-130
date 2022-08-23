from .prep import prep_hw, prep_notes

if __name__ == '__main__':
    import argparse

    description = \
        """ clears & deletes jupyter cells per string inclusion.  For example, 
        "--type hw" removes all cells with the string "rubric" or "solution".  
        see https://github.com/matthigger/ipynb_strip_copy for details """

    parser = argparse.ArgumentParser(description)
    parser.add_argument('file', type=str, nargs=1, help='input ipynb')
    parser.add_argument('-t', '--type', type=str, default='notes',
                        help='"hw" or "notes"')
    args = parser.parse_args()

    if args.type in ('hw', 'quiz'):
        prep_hw(args.file[0])
    elif args.type == 'notes':
        prep_notes(args.file[0])
    else:
        raise AttributeError('invalid type, pass either "hw" or "notes"')
