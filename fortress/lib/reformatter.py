""" Reformat a FORMAT source file

TODO:
  Check for freeform vs. fixedform code
  
"""

__date__ = "$Date: 2016/02/17 $"
__license__ = "MIT"  # Flo?
__authors__ = [
    "Florian Zwicke <z@zwicke.org>",
    "Roland Siegbert <r@rscircus.org>"
]

import sys
import re

from fortress.lib import unwrapped_line
from fortress.lib import fortress_style


class Reformatter:
    """Class that represents a Fortran source code reformatting"""

    def __init__(self, unwrapped_source=None, lines=None):
        """Function to read the source code from a file."""

        # do initializations
        self.codeLines = []
        self.isFreeForm = not fortress_style.Get('CONVERT_FIXED_TO_FREE')

        if fortress_style.Get('FIX_LINE_ENDINGS'):
            unwrapped_source.replace(r"\r\n", r"\n") # Windows
            unwrapped_source.replace(r"\r", r"\n")   # Mac OS

        lineno = 0
        # tokenize and clean up already
        for line in unwrapped_source.split("\n"):
            lineno += 1

            # Collect lines in containers
            cLine = unwrapped_line.UnwrappedLine(line, self.isFreeForm)

            # Handle line numbers
            cLine.lineNo = lineno
            if lines:
                if (lineno < lines[0][0]) or (lines[0][1] < lineno):
                    cLine.enabled = False

            # Replace tabs with spaces (args: amount of spaces)
            if fortress_style.Get('REPLACE_TABS_BY_SPACES'):
                cLine.replaceTabsBySpaces(fortress_style.Get('INDENT_WIDTH'))
            cLine.tokenize()

            # Unindent #PREPROC
            if fortress_style.Get('UNINDENT_PREPROCESSOR_DIRECTIVES'):
                cLine.unindentPreProc()

            self.codeLines.append(cLine)

        self.identifyContinuations()

    def reformat(self):
        for codeLine in self.codeLines:
            if fortress_style.Get('CONVERT_FIXED_TO_FREE'):
                codeLine.convertFixedToFree()
            if fortress_style.Get('ADD_SPACES_AROUND_OPERATORS'):
                codeLine.addSpacesInCode()
            codeLine.addOptAmpersandToCont()

        # Reindents the code(block):
        if fortress_style.Get('REINDENT'):
            self.fixIndentation(fortress_style.Get('INDENT_WIDTH'), fortress_style.Get('CONTI_INDENT_WIDTH'))
        if fortress_style.Get('ADD_REMARKS'):
            self.markLongLines(100)


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

            codeLine.setIndentation(curIndent, indent*" ")
            codeLine.leftSpace += (contiIndent*" " if codeLine.isContinuation else "")

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

        In free-form, continued lines may not be marked as such.
        Therefore, we have to ensure that every 'continued' line
        is followed by a 'continuation'.

        In fixed-form, we need to walk through the file backwards
        to identify 'continued' lines.

    Note:
      Call before stripping whitespace and indent fix.

    Definitions:
      isContinued means there exists an & at the end of a line
      isContinuation means there exists an & at the beginning of a line
    """

        if self.isFreeForm:
            inConti = False
            inTightConti = False
            for codeLine in self.codeLines:
                # is it a code line and is it after a continued line?
                if codeLine.hasCode() and inConti:
                    codeLine.isContinuation = True
                    # is it 'tightly' continued?
                    if inTightConti:
                        codeLine.isTightContinuation = True
                    inConti = False
                    inTightConti = False

                # check if line is continued
                if codeLine.isContinued:
                    inConti = True
                    # 'tightly' continued?
                    if codeLine.isTightContinued:
                        inTightConti = True

        else: # fixed form
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


    def generateCodeLines(self):
        """Generate a string from the codelines"""
        output = ""
        for cLine in self.codeLines:
            if cLine.enabled:
                output += cLine.rebuild().rstrip() + "\n"
            else:
                output += cLine.origLine.rstrip() +"\n"
        return output
