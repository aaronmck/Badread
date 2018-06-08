"""
Copyright 2018 Ryan Wick (rrwick@gmail.com)
https://github.com/rrwick/Badread

This file is part of Badread. Badread is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. Badread is distributed
in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with Badread.
If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import pathlib
import sys
from .help_formatter import MyParser, MyHelpFormatter
from .version import __version__
from .misc import bold
from . import settings


def main():
    parser = MyParser(description='Badread',
                      formatter_class=MyHelpFormatter, add_help=False)

    subparsers = parser.add_subparsers(title='Commands', dest='subparser_name')
    simulate_subparser(subparsers)
    model_subparser(subparsers)
    plot_subparser(subparsers)

    longest_choice_name = max(len(c) for c in subparsers.choices)
    subparsers.help = 'R|'
    for choice, choice_parser in subparsers.choices.items():
        padding = ' ' * (longest_choice_name - len(choice))
        subparsers.help += choice + ': ' + padding
        d = choice_parser.description
        subparsers.help += d[0].lower() + d[1:]  # don't capitalise the first letter
        subparsers.help += '\n'

    help_args = parser.add_argument_group('Help')
    help_args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                           help='Show this help message and exit')
    help_args.add_argument('--version', action='version', version=__version__,
                           help="Show program's version number and exit")

    # If no arguments were used, print the base-level help which lists possible commands.
    if len(sys.argv) == 1:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.subparser_name == 'simulate':
        check_simulate_args(args)
        from .simulate import simulate
        simulate(args)

    elif args.subparser_name == 'model':
        from .error_model import make_error_model
        make_error_model(args)

    elif args.subparser_name == 'plot':
        from .plot_window_identity import plot_window_identity
        plot_window_identity(args)


def simulate_subparser(subparsers):
    group = subparsers.add_parser('simulate', description=bold('Badread: a long read simulator '
                                                               'that can imitate many types of '
                                                               'read problems'),
                                  formatter_class=MyHelpFormatter, add_help=False)

    required_args = group.add_argument_group('Required arguments')
    required_args.add_argument('--reference', type=str, required=True,
                               help='Reference FASTA file')
    required_args.add_argument('--quantity', type=str, required=True,
                               help='Either an absolute value (e.g. 250M) or a relative depth '
                                    '(e.g. 25x)')

    sim_args = group.add_argument_group('Simulation parameters',
                                        description='Length and identity and error distributions')
    sim_args.add_argument('--length', type=str, default='10000,9000',
                          help='Fragment length distribution (mean and stdev in bp, '
                               'default: DEFAULT)')
    sim_args.add_argument('--identity', type=str, default='85,95,4',
                          help='Sequencing identity distribution (mean, max and shape, '
                               'default: DEFAULT)')
    sim_args.add_argument('--error_model', type=str, default='random',
                          help='Can be "random" (for random errors), "perfect" (for no errors) '
                               'or a filename for a read error model (for realistic errors)')

    problem_args = group.add_argument_group('Adapters',
                                            description='Controls adapter sequences on the start '
                                                        'and end of reads')
    problem_args.add_argument('--start_adapter', type=str, default='0.9,0.6',
                              help='Rate and amount for adapters on starts of reads')
    problem_args.add_argument('--end_adapter', type=str, default='0.5,0.2',
                              help='Rate and amount for adapters on ends of reads')
    problem_args.add_argument('--start_adapter_seq', type=str,
                              default='AATGTACTTCGTTCAGTTACGTATTGCT',
                              help='Adapter sequence for starts of reads')
    problem_args.add_argument('--end_adapter_seq', type=str, default='GCAATACGTAACTGAACGAAGT',
                              help='Adapter sequence for ends of reads')

    problem_args = group.add_argument_group('Problems',
                                            description='Ways reads can go wrong')
    problem_args.add_argument('--junk_reads', type=float, default=1,
                              help='This percentage of reads will be low-complexity junk')
    problem_args.add_argument('--random_reads', type=float, default=1,
                              help='This percentage of reads will be random sequence')
    problem_args.add_argument('--chimeras', type=float, default=1,
                              help='Percentage at which separate fragments join together')
    problem_args.add_argument('--glitches', type=str, default='5000,50,50',
                              help='Read glitch parameters')
    problem_args.add_argument('--small_plasmid_bias', action='store_true',
                              help='If set, then small circular plasmids are lost when the '
                                   'fragment length is too high (default: small plasmids are '
                                   'included regardless of fragment length)')

    other_args = group.add_argument_group('Other')
    other_args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit')


def model_subparser(subparsers):
    group = subparsers.add_parser('model', description='Generate error model',
                                  formatter_class=MyHelpFormatter, add_help=False)

    required_args = group.add_argument_group('Required arguments')
    required_args.add_argument('--reference', type=str, required=True,
                               help='Reference FASTA file')
    required_args.add_argument('--reads', type=str, required=True,
                               help='FASTQ of real reads')
    required_args.add_argument('--alignment', type=str, required=True,
                               help='PAF alignment of reads aligned to reference')

    required_args = group.add_argument_group('Optional arguments')
    required_args.add_argument('--k_size', type=int, default=7,
                               help='Error model k-mer size')
    required_args.add_argument('--max_alignments', type=int,
                               help='Only use this many alignments when generating error model')
    required_args.add_argument('--max_alt', type=int, default=25,
                               help='Only save up to this many alternatives to each k-mer')

    other_args = group.add_argument_group('Other')
    other_args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit')


def plot_subparser(subparsers):
    group = subparsers.add_parser('plot', description='Plot read window identities',
                                  formatter_class=MyHelpFormatter, add_help=False)

    required_args = group.add_argument_group('Required arguments')
    required_args.add_argument('--reference', type=str, required=True,
                               help='Reference FASTA file')
    required_args.add_argument('--reads', type=str, required=True,
                               help='FASTQ of real reads')
    required_args.add_argument('--alignment', type=str, required=True,
                               help='PAF alignment of reads aligned to reference')

    required_args = group.add_argument_group('Optional arguments')
    required_args.add_argument('--window', type=int, default=100,
                               help='Window size in bp')

    other_args = group.add_argument_group('Other')
    other_args.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit')


def check_simulate_args(args):
    # TODO: make sure reference exists

    model = args.error_model.lower()
    if model != 'perfect' and model != 'random':
        if not pathlib.Path(args.error_model).is_file():
            sys.exit('Error: {} is not a file\n'
                     '  --error_model must be "random", "perfect" or a '
                     'filename'.format(args.error_model))

    if args.chimeras > 50:
        sys.exit('Error: --chimeras cannot be greater than 50')
    if args.junk_reads > 100:
        sys.exit('Error: --junk_reads cannot be greater than 100')
    if args.random_reads > 100:
        sys.exit('Error: --random_reads cannot be greater than 100')
    if args.junk_reads + args.random_reads > 100:
        sys.exit('Error: --junk_reads and --random_reads cannot sum to more than 100')

    try:
        length_parameters = [float(x) for x in args.length.split(',')]
        args.mean_frag_length = length_parameters[0]
        args.frag_length_stdev = length_parameters[1]
    except (ValueError, IndexError):
        sys.exit('Error: could not parse --length values')
    if args.mean_frag_length <= settings.MIN_MEAN_READ_LENGTH:
        sys.exit('Error: mean read length must be at '
                 'least {}'.format(settings.MIN_MEAN_READ_LENGTH))
    if args.frag_length_stdev < 0:
        sys.exit('Error: read length stdev cannot be negative')

    try:
        identity_parameters = [float(x) for x in args.identity.split(',')]
        args.mean_identity = identity_parameters[0]
        args.max_identity = identity_parameters[1]
        args.identity_shape = identity_parameters[2]
    except (ValueError, IndexError):
        sys.exit('Error: could not parse --identity values')
    if args.mean_identity > 100.0:
        sys.exit('Error: mean read identity cannot be more than 100')
    if args.max_identity > 100.0:
        sys.exit('Error: max read identity cannot be more than 100')
    if args.mean_identity <= settings.MIN_MEAN_READ_IDENTITY:
        sys.exit('Error: mean read identity must be at '
                 'least {}'.format(settings.MIN_MEAN_READ_IDENTITY))
    if args.max_identity <= settings.MIN_MEAN_READ_IDENTITY:
        sys.exit('Error: max read identity must be at '
                 'least {}'.format(settings.MIN_MEAN_READ_IDENTITY))
    if args.mean_identity > args.max_identity:
        sys.exit('Error: mean identity ({}) cannot be larger than max '
                 'identity ({})'.format(args.mean_identity, args.max_identity))
    if args.identity_shape <= 0.0:
        sys.exit('Error: read identity shape must be a positive value')

    try:
        glitch_parameters = [float(x) for x in args.glitches.split(',')]
        args.glitch_rate = glitch_parameters[0]
        args.glitch_size = glitch_parameters[1]
        args.glitch_skip = glitch_parameters[2]
    except (ValueError, IndexError):
        sys.exit('Error: could not parse --glitches values')
    if args.glitch_rate < 0 or args.glitch_size < 0 or args.glitch_skip < 0:
        sys.exit('Error: --glitches must contain non-negative values')


if __name__ == '__main__':
    main()
