#! /usr/bin/env python3
"""Find And Replace in Files (nieuwe naam: Farft ?)
"""
import sys
import argparse
from afrift.base import main


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, epilog="""\
    file type specfic context is NOT some surrounding lines, but a characteristic
    of the location, e.g. the function in which a line is found
    """)
    parser.add_argument("fname", nargs="*", help='one or more path names')
    parser.add_argument("-m", "--appmode", default='', choices=['single', 'multi'],
                        help='specify execution mode')
    parser.add_argument("-s", "--search", help="search argument")
    parser.add_argument("-r", "--replace", help="replacement")
    parser.add_argument("-X", "--regex", action='store_true',
                        help="argument is regular expression")
    parser.add_argument("-C", "--case-sensitive", action='store_true',
                        help="case-sensitive search")
    parser.add_argument("-W", "--whole-words", action='store_true',
                        help="search for whole words only")
    parser.add_argument("-R", "--recursive", action='store_true',
                        help="search directories recursively")
    parser.add_argument("-S", "--follow-symlinks", action='store_true',
                        help="search in symlinked files")
    parser.add_argument("-D", "--select-subdirs", action='store_true',
                        help="ask for subdirectories to search in")
    parser.add_argument("-F", "--select-files", action='store_true',
                        help="ask for files to search in")
    parser.add_argument("-e", "--extensions", help="filter on file extension(s)")
    parser.add_argument("-P", "--python-context", action='store_true',
                        help="show context (file type specific)")
    parser.add_argument("-B", "--backup-originals", action='store_true',
                        help="backup original files when replacing")
    parser.add_argument("-U", "--use-saved", action='store_true',
                        help="use saved search options")
    parser.add_argument("-I", "--dont-save", action='store_true',
                        help="do not update saved search options")
    parser.add_argument("-N", "--no-gui", action='store_true',
                        help="don't show initial parameters screen")
    parser.add_argument("-o", "--output-file", type=argparse.FileType('w'),
                        help="save output to file")
    parser.add_argument("-p", "--full-path", action='store_true',
                        help="show full paths in output")
    parser.add_argument("-c", "--as-csv", action='store_true',
                        help="output as csv")
    parser.add_argument("-u", "--summarize", action='store_true',
                        help="output_summarized")
    args = parser.parse_args()
    sys.exit(main(vars(args)))
