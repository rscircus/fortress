"""Interface to file resources.

This module provides functions for interfacing with files:
  * opening
  * writing
  * querying

"""

import fnmatch
import os
import re

from lib2to3.pgen2 import tokenize
from fortress.lib import py3compat


def WriteReformattedCode(filename, reformatted_code, in_place, encoding):
  """Emit the reformatted code.

  Write the reformatted code into the file, if in_place is True. Otherwise,
  write to stdout.

  Arguments:
    filename         : (unicode) The name of the unformatted file.
    reformatted_code : (unicode) The reformatted code.
    in_place         : (bool) If True, then write the reformatted code to the file.
    encoding         : (unicode) The encoding of the file.
  """
  if in_place:
    with py3compat.open_with_encoding(filename,
                                      mode='w',
                                      encoding=encoding) as fd:
      fd.write(reformatted_code)
  else:
    py3compat.EncodeAndWriteToStdout(reformatted_code, encoding)


def GetCommandLineFiles(command_line_file_list, recursive, exclude):
  """Return the list of files specified on the command line."""
  return _FindFortranFiles(command_line_file_list, recursive, exclude)


def IsFortranOrHeaderFile(filename, headers_too=True):
  """Return True if filename is a Fortran file."""
  if headers_too:
    if os.path.splitext(filename)[1] in ['.F','.F90','.f','f90','h']:
      return True
  elif os.path.splitext(filename)[1] in ['.F','.F90','.f','f90']:
    return True

  try:
    with open(filename, 'rb') as fd:
      encoding = tokenize.detect_encoding(fd.readline)[0]

    # Check for correctness of encoding.
    with py3compat.open_with_encoding(filename, encoding=encoding) as fd:
      fd.read()
  except UnicodeDecodeError:
    encoding = 'latin-1'
  except (IOError, SyntaxError):
    # If we fail to detect encoding (or the encoding cookie is incorrect - which
    # will make detect_encoding raise SyntaxError), assume it's not a Fortran
    # file.
    return False

  try:
    with py3compat.open_with_encoding(filename,
                                      mode='r',
                                      encoding=encoding) as fd:
      first_line = fd.readlines()[0]
  except (IOError, IndexError):
    return False

  # In all other cases assume everything is worse.
  return False


def _FindFortranFiles(filenames, recursive, exclude):
  """Find all Fortran files."""
  fortran_files = []
  for filename in filenames:
    if os.path.isdir(filename):
      if recursive:
        fortran_files.extend(
            os.path.join(dirpath, f)
            for dirpath, _, filelist in os.walk(filename) for f in filelist
            if IsFortranOrHeaderFile(os.path.join(dirpath, f)))
      else:
        raise Exception(
            "directory specified without '--recursive' flag: %s" % filename)
    elif os.path.isfile(filename):
      # Assuming user knows what s/he does
      fortran_files.append(filename)

  if exclude:
    return [f
            for f in fortran_files
            if not any(fnmatch.fnmatch(f, p) for p in exclude)]

  return fortran_files
