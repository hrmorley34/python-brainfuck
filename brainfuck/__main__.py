import argparse
import sys
from .brainfuck import BytesBrainfuck


parser = argparse.ArgumentParser()

scriptgroup = parser.add_mutually_exclusive_group(required=True)
scriptgroup.add_argument(
    "-f",
    "--script",
    metavar="FILE",
    type=argparse.FileType("r"),
    dest="scriptfile",
    help="Script file",
)
scriptgroup.add_argument(
    "-c",
    "--command",
    metavar="SCRIPT",
    type=str,
    dest="command",
    help="Script",
)

parser.add_argument(
    "-i",
    "--infile",
    metavar="FILE",
    type=argparse.FileType("rb"),
    default=sys.stdin.buffer,
    dest="infile",
    help="Input data for the script (default: read from stdin)",
)

parser.add_argument(
    "-o",
    "--output",
    metavar="FILE",
    type=argparse.FileType("wb"),
    default=sys.stdout.buffer,
    dest="outfile",
    help="Output file for the script (default: write to stdout)",
)


def main(args: argparse.Namespace):
    if args.command is not None:
        script = args.command
    elif args.scriptfile is not None:
        script = args.scriptfile.read()
        args.scriptfile.close()
    else:
        raise Exception

    b = BytesBrainfuck(script, args.infile, args.outfile)
    b.run()


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
