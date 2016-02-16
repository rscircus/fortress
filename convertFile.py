#!/usr/bin/env python
#########################################################################
# This script uses the CodeFile library to read a fixed-form Fortran
# source file and convert it to free-form.
#
# ToDo:
# - none
#
# created by Florian Zwicke, Feb. 10, 2016
#########################################################################

import time
import sys

from CodeFile import *

def transformFile(oldFile, newFile):
  """Return cleaned newFile from oldFile."""
  # read in file
  # args: fileName, isFreeForm, hint="", replaceTabs=True, unindentPreProc=True
  codeFile = CodeFile(oldFile, isFreeForm=True, hint="REMARK")

# TODO: Shift into CodeFile, s.t. codeLine can be arbitrary
  for codeLine in codeFile.codeLines:
# TODO: Identify and automate Fixed vs. Free
    #codeLine.convertFixedToFree()
    codeLine.addSpacesInCode()
    #codeLine.fixDeclarationsInCode()
    codeLine.stripTrailingWhitespace()

  # converter control
  codeFile.fixIndentation("    ", 2)
  codeFile.markLongLines(100)

  # output file
  codeFile.write()

#########################################################################
# Main program                                                          #
#########################################################################

# is a filename given?
#if len(sys.argv) < 3:
#  print("Usage: " + sys.argv[0] + " oldfile newfile")
#  exit()
#oldFile = sys.argv[1]
#newFile = sys.argv[2]

if len(sys.argv) < 2:
  print("Usage: " + sys.argv[0] + " file1.F file2.F ... fileN.F")
  print("or " + sys.argv[0] + " *.F ")
  exit()

for file in sys.argv[1:]:
  print "Converting file '" + file + "'..."
  transformFile(file, file)


# output status message
#print("! created by " + sys.argv[0] + " from source file " + filename)
#print("! on " + time.strftime("%c"))
