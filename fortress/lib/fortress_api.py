"""Entry points for FORTRESS.

The main APIs that FORTRESS exposes to drive the reformatting.

  FormatFile(): reformat a file.
  FormatCode(): reformat a string of code.

These APIs have some common arguments:

  lines: (list of tuples of integers) A list of tuples of lines, [start, end],
    that we want to format. The lines are 1-based indexed. It can be used by
    third-party code (e.g., IDEs) when reformatting a snippet of code rather
    than a whole file.

  print_diff: (bool) Instead of returning the reformatted source, return a
    diff that turns the formatted source into reformatter source.
"""

import difflib
import re
import sys

from fortress.lib import file_resources # Writing and reading files
from fortress.lib import reformatter    # Doing the real work
from fortress.lib import py3compat
from fortress.lib import fortress_style

from lib2to3.pgen2 import tokenize      # For encoding in ReadFile - alt: chardet

def FormatFile(filename,
               lines=None,
               print_diff=False,
               in_place=False,
               logger=None):
  """Format a single Fortran file and return the formatted code.

  Arguments:
    filename  : (unicode) The file to reformat.
    lines     : (tuple) Lines to reformat
    in_place  : (bool) If True, write the reformatted code back to the file.
    logger    : (io streamer) A stream to output logging.
    remaining : see comment at the top of this module.

  Returns:
    Tuple of (reformatted_code, encoding, changed). reformatted_code is None if
    the file is sucessfully written to (having used in_place). reformatted_code
    is a diff if print_diff is True.

  Raises:
    IOError    : raised if there was an error reading the file.
    ValueError : raised if in_place and print_diff are both specified.
  """
  _CheckPythonVersion()

  if in_place and print_diff:
    raise ValueError('Cannot pass both in_place and print_diff.')

  original_source, encoding = ReadFile(filename, logger)

  # Reformat code:
  reformatted_source, changed = FormatCode(original_source,
                                           filename=filename,
                                           lines=lines,
                                           print_diff=print_diff)
  if in_place:
    if original_source:
      file_resources.WriteReformattedCode(filename, reformatted_source,
                                          in_place, encoding)
    return None, encoding, changed

  return reformatted_source, encoding, changed


def FormatCode(unformatted_source,
               filename='<unknown>',
               lines=None,
               print_diff=False):
  """Format a string of Fortran code.

  This provides an alternative entry point to FORTRESS.

  Arguments:
    unformatted_source  : (unicode) The code to format.
    filename            : (unicode) The name of the file being reformatted.
    remaining arguments : see comment at the top of this module.

  Returns:
    Tuple of (reformatted_source, changed). reformatted_source conforms to the
    desired formatting style. changed is True if the source changed.
  """
  _CheckPythonVersion()

  if not unformatted_source.endswith('\n'):
    unformatted_source += '\n'

  # Reformat:
  Reform = reformatter.Reformatter(unformatted_source, lines)
  Reform.reformat()
  reformatted_source = Reform.generateCodeLines()

  if unformatted_source == reformatted_source:
    return '' if print_diff else reformatted_source, False

  # Diff:
  code_diff = _GetUnifiedDiff(unformatted_source,
                              reformatted_source,
                              filename=filename)

  if print_diff:
    return code_diff, code_diff != ''

  return reformatted_source, True


def ReadFile(filename, logger=None):
  """Read the contents of the file.

  An optional logger can be specified to emit messages to your favorite logging
  stream. If specified, then no exception is raised. This is external so that it
  can be used by third-party applications.

  Arguments:
    filename: (unicode) The name of the file.
    logger:  (function) A function or lambda that takes a string and emits it.

  Returns:
    The contents of filename.

  Raises:
    IOError: raised if there was an error reading the file.
  """
  try:
    with open(filename, 'rb') as fd:
      encoding = tokenize.detect_encoding(fd.readline)[0]
  except IOError as err:
    if logger:
      logger(err)
    raise

  try:
    with py3compat.open_with_encoding(filename,
                                      mode='r',
                                      encoding=encoding) as fd:
      source = fd.read()
    return source, encoding
  except IOError as err:
    if logger:
      logger(err)
    raise


def _GetUnifiedDiff(before, after, filename='code'):
  """Get a unified diff of the changes.

  Arguments:
    before   : (unicode) The original source code.
    after    : (unicode) The reformatted source code.
    filename : (unicode) The code's filename.

  Returns:
    The unified diff text.
  """
  before = before.splitlines()
  after = after.splitlines()
  return '\n'.join(difflib.unified_diff(before,
                                        after,
                                        filename,
                                        filename,
                                        '(original)',
                                        '(reformatted)',
                                        lineterm='')) + '\n'

def _CheckPythonVersion():
  errmsg = 'FORTRESS is only supported by Python 2.6 or 3.4+'
  if sys.version_info[0] == 2:
    if sys.version_info[1] < 6:
      raise RuntimeError(errmsg)
  elif sys.version_info[0] == 3:
    if sys.version_info[1] < 4:
      raise RuntimeError(errmsg)

