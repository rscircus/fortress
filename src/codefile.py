#!/usr/bin/env python2
"""This is a library to lint and modernize Fortran source files.

Note:
  Needs some kind of front end.

Todo:
  - Create some variables for regular expressions that are used multiple
    times.
  - Currently, '&' signs at the endings of lines are not recognized as
    continued line when parsing free-form code.
  - Check if statement checks for indentation are complete.
  - Check if 'where' statements are matched correctly.
  - Operator matching usually does not work at beginnings or endings
    of parts.
  - CodeStatement for (cont.) statement identification
  - Split codeline into FreeLine and FixedLine
  - Statements only in Free (after conversion)
  - Move parseLine into constructor - DONE: 2016-02-16 Tue 10:30 @roland
  - Reinsert execution position for functions (PARSE LINE?) @roland
  - Note that the ampersand at the beginning of lines is optional
  - in free-form. This is currently not supported by this script.
"""

__date__    = "$Date: 2016/02/17 $"
__license__ = "MIT" # Flo?
__authors__ = [
    "Florian Zwicke <z@zwicke.org>",
    "Roland Siegbert <r@rscircus.org>"
    ]

import sys
import re
from codeline import codeline

class codefile:
  """Class that represents a Fortran source code file"""

  def __init__(self, fileName, isFreeForm, hint="", replaceTabs=True,
               unindentPreProc=True):
    """Function to read the source code from a file."""
    # try to open and read file
    try:
      with open(fileName) as file:
        content = file.readlines()
    except IOERROR:
      print("Error: File inaccesible")
      sys.exit(0)

    # do initializations
    self.codeLines = []
    self.fileName = fileName

    # parse and clean up already
    for line in content:
      cLine = codeline(line, isFreeForm, hint)

      # Replace tabs with spaces (args: amount of spaces)
      if replaceTabs:
        cLine.replaceTabs(8)
      cLine.parseLine()

      # Unindent preprocessor directives
      if unindentPreProc:
        cLine.unindentPreProc()
      self.codeLines.append(cLine)

    self.identifyContinuations()

  def fixIndentation(self, indent, contiIndent):
    """Change the indentation of a codeLine.

    Note:
        This makes sense in free-form code only.

    Args:
      indent (int): new indent length

    """
    curIndent = 0
    for codeLine in self.codeLines:
      if codeLine.decreasesIndentBefore():
        curIndent -= 1
      if curIndent < 0:
        codeLine.remarks.append("Negative indentation level reached.")
        curIndent = 0

      codeLine.setIndentation(curIndent + \
          (contiIndent if codeLine.isContinuation else 0), indent)

      if codeLine.increasesIndentAfter():
        curIndent += 1

      codeLine.preserveCommentPosition()

    # back at zero indentation?
    if curIndent > 0:
      self.codeLines[-1].remarks.append("Positive indentation level remaining.")

  def markLongLines(self, allowedLength):
    """Mark lines above allowedLength.

    Note:
      Has to be called at the end.

    """
    for codeLine in self.codeLines:
      if codeLine.getLength() > allowedLength:
        codeLine.remarks.append("Line above is longer than " + str(allowedLength) \
            + " characters.")

  def identifyContinuations(self):
    """Identify continuated lines.

    Note:
      Call before stripping whitespace and indent fix.

    """
    # go through lines in reverse order
    inConti = False
    inTightConti = False
    for codeLine in reversed(self.codeLines):
      # is it a code line and is it followed by continuation?
      if codeLine.hasCode() and inConti:
        codeLine.isContinued = True
        # is it a 'tight' continuation?
        if inTightConti and not len(codeLine.commentSpace) \
            and len(codeLine.rightSpace) == 1:
          codeLine.isTightContinued = True
        inConti = False
        inTightConti = False

      # check if line is continuation
      if codeLine.isContinuation:
        inConti = True
        # is it a 'tight' continuation?
        if not codeLine.isFreeForm and not len(codeLine.leftSpace):
          codeLine.isTightContinuation = True
          inTightConti = True

  def write(self):
    """Rebuild & write source CodeFile from codelines."""
    output = ""

    for codeLine in self.codeLines:
      output += codeLine.rebuild()

    # output file
    fOut = open(self.fileName, "w")
    fOut.write(output)
    fOut.close()




