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

  # exchange with line above to disable output of warnings
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

if len(sys.argv) < 2:
  print("Usage: " + sys.argv[0] + " file1.F file2.F ... fileN.F")
  print("or " + sys.argv[0] + " *.F ")
  exit()

for file in sys.argv[1:]:
  print "Converting file '" + file + "'..."
  transformFile(file, file)
