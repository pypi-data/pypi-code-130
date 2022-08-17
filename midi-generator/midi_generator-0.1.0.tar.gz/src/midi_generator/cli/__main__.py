import argparse
from itertools import chain, combinations

class CustomParser(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
                 kwargs.get('prog'),
                 indent_increment=2,
                 max_help_position=100,
                 width=None)

    def _format_action(self, action):
        result = super()._format_action(action)
        if isinstance(action, argparse._SubParsersAction):
            # fix indentation on first line
            return "%*s%s" % (self._current_indent, "", result.lstrip())
        return result

    def _format_action_invocation(self, action):
        if isinstance(action, argparse._SubParsersAction):
            # remove metavar and help line
            return ""
        return super()._format_action_invocation(action)

    def _iter_indented_subactions(self, action):
        if isinstance(action, argparse._SubParsersAction):
            try:
                get_subactions = action._get_subactions
            except AttributeError:
                pass
            else:
                # remove indentation
                yield from get_subactions()
        else:
            yield from super()._iter_indented_subactions(action)


def powerset(iterable):
    return list(map(lambda x: list(x), chain.from_iterable(combinations(iterable, r) for r in range(len(iterable)+1))))


def print_cli():
    parser = argparse.ArgumentParser(prog="midi-generator", 
                            description='Command line interface for b2bAI.', 
                            usage='%(prog)s [OPTIONS] COMMAND', 
                            epilog="Run 'midi-generator COMMAND --help' for more information on a command.",
                            formatter_class=CustomParser)

    parser.add_argument('-v', '--verbose', action='store_true', help='print the logbook')

    subparsers = parser.add_subparsers(title='commands')

    generate = subparsers.add_parser('generate', 
                                description='Generate a MIDI file from a given configuration.',
                                help='generate a MIDI file',
                                usage='%(prog)s [OPTIONS] generate {FILE|OPTIONS}', 
                                formatter_class=CustomParser)

    generate.add_argument('-c', '--config', 
                    type=str, 
                    help='the configuration file', 
                    metavar='File')

    generate.add_argument('--bars', 
                    type=int, 
                    metavar='{4|8}',
                    help='the number of bars to generate', 
                    choices=[4, 8], 
                    default=4)

    generate.add_argument('--rates',
                    type=list[float], 
                    metavar='list[float]',
                    help='the note lengths used to generate the MIDI file', 
                    choices=powerset([1, 1/2, 1/4, 1/8, 1/16]),
                    default=[1/4, 1/8])

    generate.add_argument('--scale',
                    type=str,
                    metavar='Scale',
                    help='the scale in which to generate the MIDI file',
                    default='C minor')

    generate.add_argument('--density',
                    type=float,
                    metavar='float',
                    help='the density of notes in the generated MIDI file',
                    default=0.4)

    generate.add_argument('--syncopation',
                    type=float,
                    metavar='float',
                    help='the level of syncopation in the generated MIDI file',
                    default=0.3)

    generate.add_argument('--ispolyphonic', 
                    action='store_true',
                    help='whether to generate a polyphonic or monophonic MIDI file',
                    default=False)
                    
    mutate = subparsers.add_parser('mutate', 
                            description='Mutate a given MIDI file.',
                            usage='%(prog)s [OPTIONS] generate FILE [OPTIONS]', 
                            help='mutate a MIDI file.',
                            formatter_class=CustomParser)

    mutate.add_argument('file', 
                    type=str, 
                    help='file containing sequence to mutate')

    mutate.add_argument('--probability',
                    type=float,
                    metavar='float',
                    help='the probability of mutating a note',
                    default=0.1)
                    
    continue_seq = subparsers.add_parser('continue', 
                            description='Continue a given MIDI sequence.',
                            usage='%(prog)s [OPTIONS] generate FILE [OPTIONS]', 
                            help='continue a MIDI sequence.',
                            formatter_class=CustomParser)

    continue_seq.add_argument('file', 
                    type=str, 
                    help='file containing sequence to continue')
                    
    args = parser.parse_args()
