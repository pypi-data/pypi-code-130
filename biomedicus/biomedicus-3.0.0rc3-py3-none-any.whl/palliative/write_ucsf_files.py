import csv
from pathlib import Path

import sys

def write_out(infile, outdir, count):
    outdir = Path(outdir)
    with open(infile) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        i = 0
        for row in reader:
            id = row[0]
            text = row[5].replace('\t', '\n')
            outfile = (outdir / (id + ".txt"))
            with outfile.open('w') as outp:
                print('writing to' + str(outfile))
                outp.write(text)
            i = i + 1
            if i >= count:
                break


if __name__ == '__main__':
    indir = sys.argv[1]
    outdir = sys.argv[2]
    count = int(sys.argv[3])
    write_out(indir, outdir, count)
