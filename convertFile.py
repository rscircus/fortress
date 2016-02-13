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

#########################################################################
# Function to transform file                                            #
#########################################################################

def transformFile(oldFile, newFile):
  # read in file
  codeFile = CodeFile(oldFile, False, "REMARK")

  # exchange with line above to ignore long lines
  #codeFile = CodeFile(oldFile, False)

  # convert
  for codeLine in codeFile.codeLines:
    codeLine.replaceTabs(8)
    codeLine.parseLine()
    codeLine.unindentPreProc()
    codeLine.verifyContinuation()

  codeFile.identifyContinuations()

  for codeLine in codeFile.codeLines:
    codeLine.convertFixedToFree()
    codeLine.addSpacesInCode()
    #codeLine.fixDeclarationsInCode()
    codeLine.swallowLengthChange()
    codeLine.stripTrailingWhitespace()

  # converter control
  codeFile.fixIndentation("    ", 2)
  #codeFile.transformDoxygenBlocks(100)
  codeFile.markLongLines(100)

  # output file
  fOut = open(newFile, "w")
  fOut.write(codeFile.rebuild())
  fOut.close()

#########################################################################
# Main program                                                          #
#########################################################################

## is a path given?
#if len(sys.argv) < 2:
#  print("Usage: " + sys.argv[0] + " oldpath newpath")

# is a filename given?
if len(sys.argv) < 3:
  print("Usage: " + sys.argv[0] + " oldfile newfile")
  exit()
oldFile = sys.argv[1]
newFile = sys.argv[2]

transformFile(oldFile, newFile)

# output status message
#print("! created by " + sys.argv[0] + " from source file " + filename)
#print("! on " + time.strftime("%c"))
