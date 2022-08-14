#!/usr/bin/python3

"""Plot multiple keys on multiple graphs in an pyfsdb/FSDB file.

`multi-key-graph` is designed to:

1. read in time-series data in FSDB format (from pyfsdb: tab-separated with a header)
2. Plot data in columns (-c COLNAME1 ...) for a given key column value (-k KEY).
3. Which key values to be plotted can be limited to a fixed list (-l VAL1 VAL2 ...)
4. Save the results to an output PNG file (-o OUT.png) or a window (-i)

If multiple columns are specified, the output will contain multiple
vertically stacked graphs with aligned X-axes allowing for easier
comparison of noisy time-series plots.

Plot labels can be specified using -T TITLE, --xlabel X-LABEL, and
--ylabel Y-LABEL.  By default line plots are drawn, unless a
dotted/scatter plot (-s) is requested.  Data should be pre-sorted for
line graphs.

A list of name=replacement values can be passed for legende name
replacements (-L name=replacement).  Anonymization of key values may
be specified with an anonymization pattern that includes a %d
specifier (-A "some%d").
"""

import multikeygraph
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
import sys

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            description=__doc__, prog='multi-key-graph',
	                        epilog="Exmaple Usage: multi-key-graph -k stock -c value -l GOOGL AAPL MSFT -i market.fsdb")

    parser.add_argument("-t", "--time-column", default="timestamp", type=str,
                        help="Name of the time(stamp) column")

    parser.add_argument("-k", "--key-column", default="key", type=str,
                        help="Name of the key column")

    parser.add_argument("-c", "--columns", type=str, nargs="+",
                        help="The column name(s) to graph")

    parser.add_argument("-C", "--column-names", nargs="*", type=str,
                        help="Column name replacements to use in the graphical titles")

    parser.add_argument("-o", "--output-file", type=str,
                        help="Output file to create (eg: graph.png)")

    parser.add_argument("-l", "--limit-keys", nargs="*", type=str,
                        help="Limit the keys plotted to just these")

    parser.add_argument("--xlabel", type=str, default="Time",
                        help="xlabel for the graph")

    parser.add_argument("--ylabel", type=str, default="Count",
                        help="ylabel for the graph")

    parser.add_argument("-T", "--title", type=str, 
                        help="Title for the graph")

    parser.add_argument("-s", "--scatter", action="store_true",
                        help="Use a scatter plot (no lines)")

    parser.add_argument("-d", "--use-dots", action="store_true",
                        help="Use dots for markers instead of symbols")

    parser.add_argument("-D", "--no-dates", action="store_true",
                        help="Don't translate X labels to dates")

    parser.add_argument("-a", "--anonymize-name-pattern", type=str,
                        help="A pattern with a %%d in it to anonymize legend names")

    parser.add_argument("-L", "--legend-names", type=str, nargs="*",
                        help="key=replacement-name pairs to use in the legend; if a key isn't in the list, then the name will not be replaced.")

    parser.add_argument("-N", "--no-legend", action="store_true",
                        help="Skip the legend (default for greater than 10 items).  If greater than 10 items, this will force the legend back on.")

    parser.add_argument("-O", "--legend-outside", action="store_true",
                        help="Put the legend outside the graph (narrowing the graph)")

    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Display a window (interactive) instead of save to file")

    parser.add_argument("-m", "--time-markers", type=int, nargs="*",
                        help="draw vertical lines at these unix-epoch time markers")
    
    parser.add_argument("-ms", "--marker-size", default=10.0, type=float,
                        help="point marker size for graphs")

    parser.add_argument("-lw", "--line-width", default=3.0, type=float,
                        help="line-width to use for line graphs")

    parser.add_argument("--yrange", default=None, type=float, nargs=2,
                        help="A low and high value to use for the y-axis range (for all graphs)")

    parser.add_argument("--dont-reformat-values", action="store_true",
                        help="Don't reformat labels with K/M/G/P suffixes")

    parser.add_argument("--opacity", default=1.0, type=float,
                        help="Opacity to use when plotting")

    parser.add_argument("input_files", type=FileType('r'),
                        nargs='+', default=sys.stdin,
                        help="File to read")

    args = parser.parse_args()

    if not args.output_file and not args.interactive:
        raise ValueError("A output file (-o) or interactive (-i) is required")

    if not args.columns or len(args.columns) < 1:
        raise ValueError("Columns to graph (-c) is required")

    args.legend_map = {}
    if args.legend_names:
        for namemap in args.legend_names:
            (key, label) = namemap.split("=")
            if not key or not label:
                raise ValueError("Illegal value to --legend-names: %s" % (namemap))
            args.legend_map[key] = label

    args.column_map = {}
    if args.column_names:
        for namemap in args.column_names:
            (key, label) = namemap.split("=")
            if not key or not label:
                raise ValueError("Illegal value to --column-names: %s" % (namemap))
            args.column_map[key] = label

    return args


def main():
    args = parse_args()

    m = multikeygraph.MultiKeyGraph()

    m.graph(args.input_files,
            args.columns,
            args.time_column, args.key_column, args.limit_keys,
            args.title,
            args.anonymize_name_pattern, args.legend_map,
            args.interactive, args.output_file,
            args.xlabel, args.ylabel, args.scatter,
            args.time_markers, marker_size=args.marker_size,
            no_legend=args.no_legend,
            legend_outside=args.legend_outside,
            column_map=args.column_map,
            use_dots=args.use_dots,
            line_width=args.line_width,
            yrange=args.yrange,
            dont_reformat_values=args.dont_reformat_values,
            opacity=args.opacity,
            no_dates=args.no_dates)

if __name__ == "__main__":
    main()


