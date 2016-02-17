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
  # args: fileName, isFreeForm, hint="", replaceTabs=True, unindentPreProc=True
  codeFile = CodeFile(oldFile, isFreeForm=True, hint="REMARK")

  # exchange with line above to disable output of warnings
  #codeFile = CodeFile(oldFile, False)

  # convert
  for codeLine in codeFile.codeLines:
    codeLine.convertFixedToFree()
    codeLine.addSpacesInCode()
    #codeLine.fixDeclarationsInCode()
    codeLine.stripTrailingWhitespace()

  # converter control
  codeFile.fixIndentation("    ", 2)
  codeFile.markLongLines(100)

  # output file
  codeFile.write()

  # lint file in the end
  codeLint = codeLinter(oldFile)
  codeLint.lint()

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
