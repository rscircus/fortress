"""FORTRESS.

FORTRESS is a FORTRAN formatter, which is also able to modernize old code.

Many ideas are borrowed from Google's Python Code Formatter YAPF.

If no input file is specified, FORTRESS reads the code from STDIN.
"""
import argparse
import logging
import os
import sys
import textwrap

from fortress.lib import fortress_api
from fortress.lib import file_resources
from fortress.lib import py3compat
from fortress.lib import fortress_style

__version__ = '0.2'
__authors__ = [
    "Roland Siegbert <r@rscircus.org>"
    "Florian Zwicke <z@zwicke.org>"
    ]

def main(argv):
  """Main program.

  Arguments:
    argv: command-line arguments, such as sys.argv 
    (including the program name
      in argv[0]).

  Returns:
    0 if there were no changes, non-zero otherwise.
  """
  parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                   description = textwrap.dedent('''\
                                   FORTRESS is a formatter/modernizer of legacy FORTRAN code.
                                   ----------------------------------------------------------

                                     By default it prints the reformatted code
                                     to STDOUT. For other options see below.
                                   '''))

# TODO: line-wrapping instead of single-string
# Arguments:
  parser.add_argument('-v',
                      '--version',
                      action='store_true',
                      help='show version')

# Either diff or in-place
  diff_inplace_group = parser.add_mutually_exclusive_group()
  diff_inplace_group.add_argument('-d',
                                  '--diff',
                                  action='store_true',
                                  help='print the diff for the fixed source')
  diff_inplace_group.add_argument('-i',
                                  '--in-place',
                                  action='store_true',
                                  help='make changes to files in place')

# Either recursive or linespecific (single file)
  lines_recursive_group = parser.add_mutually_exclusive_group()
  lines_recursive_group.add_argument('-r',
                                     '--recursive',
                                     action='store_true',
                                     help='run recursively over dirs')
  lines_recursive_group.add_argument('-l',
                                     '--lines',
                                     metavar='START-END',
                                     action='append',
                                     default=None,
                                     help='range of lines to reformat; 1-based')

  parser.add_argument('-e',
                      '--exclude',
                      metavar='PATTERN',
                      action='append',
                      default=None,
                      help='patterns for files to exclude from formatting')

# TODO: Idea: Can be set as default if style.ini is present.
  parser.add_argument('-s',
                      '--style',
                      action='store',
                      default=None,
                      help='specify formatting style via local style.ini')

  parser.add_argument('--strict',
                      action='store_true',
                      help='applies all available formatting options / style.ini will be ignored')

  parser.add_argument('-t',
                      '--lint',
                      action='store_true',
                      help='lint files')

  parser.add_argument('files', nargs='*')

# Catch arguments:
  args = parser.parse_args(argv[1:])

# -v: Version
  if args.version:
    print('fortress {}'.format(__version__))
    return 0

# -l: Range of lines (begging w/ 1)
  if args.lines and len(args.files) > 1:
    parser.error('cannot use -l/--lines with more than one file')

  lines = getLines(args.lines) if args.lines is not None else None

# -s: Style file provided
  if args.strict:
    fortress_style.SetGlobalStyle(fortress_style.CreateStrictStyle())
  else:
    if args.style:
      fortress_style.SetGlobalStyle(fortress_style.CreateStyleFromConfig(args.style))
    else:
      fortress_style.SetGlobalStyle(fortress_style.CreateFortran2003Style())


# Lines case:
  if not args.files:
    if args.in_place or args.diff:
      parser.error('cannot use --in-place or --diff flags when reading '
                   'from stdin')
    original_source = []

    while True:
      try:
        # Use 'raw_input' instead of 'sys.stdin.read', because otherwise the
        # user will need to hit 'Ctrl-D' more than once if they're inputting
        # the program by hand.
        original_source.append(py3compat.raw_input())
      except EOFError:
        break

    reformatted_source, changed = fortress_api.FormatCode(
          py3compat.unicode('\n'.join(original_source) + '\n'),
          filename='<stdin>',
          lines=lines)

    # STDOUT:
    sys.stdout.write(reformatted_source)

    return 2 if changed else 0

# Recursive or file list case:
  files = file_resources.GetCommandLineFiles(args.files,
                                             args.recursive,
                                             args.exclude)
  changed = FormatFiles(files,
                        lines,
                        in_place=args.in_place,
                        print_diff=args.diff)
  return 2 if changed else 0


# TODO: Error handling in getLines
def getLines(line_strings):
  """Parses the start and end lines from a line string like 'start-end'.

  Arguments:
    line_strings: (array of string) A list of strings representing a line
      range like 'start-end'.

  Returns:
    A list of tuples of the start and end line numbers.

  Raises:
    ValueError: If the line string failed to parse or was an invalid line range.
  """
  lines = []
  for line_string in line_strings:
    line = list(map(int, line_string.split('-', 1)))
    if line[0] < 1:
      pass
    if line[0] > line[1]:
      pass
    lines.append(tuple(line))
  return lines


def FormatFiles(filenames,
                lines,
                in_place=False,
                print_diff=False):
  """Format a list of files.

  Arguments:
    filenames: (list of unicode) A list of files to reformat.

    lines: (list of tuples of integers) A list of tuples of lines, [start, end],
      that we want to format. The lines are 1-based indexed. This argument
      overrides the 'args.lines'. It can be used by third-party code (e.g.,
      IDEs) when reformatting a snippet of code.

    in_place: (bool) Modify the files in place.

    print_diff: (bool) Instead of returning the reformatted source, return a
      diff that turns the formatted source into reformatter source.

    True if the source code changed in any of the files being formatted.
  """
  changed = False
  for filename in filenames:
    logging.info('Reformatting %s', filename)
    try:
      reformatted_code, encoding, has_change = fortress_api.FormatFile(
          filename,
          in_place=in_place,
          lines=lines,
          print_diff=print_diff,
          logger=logging.warning)
      changed |= has_change
    except SyntaxError as e:
      e.filename = filename
      raise
    if reformatted_code is not None:
      file_resources.WriteReformattedCode(filename, reformatted_code, in_place,
                                          encoding)
  return changed


# TODO: Error handling
def run_main():
    sys.exit(main(sys.argv))

if __name__ == '__main__':
  run_main()
