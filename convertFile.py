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
# Main program                                                          #
#########################################################################

# is a filename given?
if len(sys.argv) < 2:
  print("Usage: " + sys.argv[0] + " filename")
  exit()
filename = sys.argv[1]
# output status message
print("! created by " + sys.argv[0] + " from source file " + filename)
print("! on " + time.strftime("%c"))

# read in file
codeFile = CodeFile(filename, False)

# convert
for codeLine in codeFile.codeLines:
  codeLine.replaceTabs(8)
  codeLine.parseLine()
  codeLine.stripTrailingWhitespace()
  codeLine.unindentPreProc()

codeFile.identifyContinuations()

for codeLine in codeFile.codeLines:
  codeLine.convertFixedToFree()
  codeLine.addSpacesInCode()
  codeLine.fixDeclarationsInCode()

codeFile.fixIndentation("    ", 2)
codeFile.markLongLines(80)

# output file
print codeFile.rebuild()
