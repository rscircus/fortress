#!/usr/bin/env python
#########################################################################
# This is a library to parse Fortran source files.
#
# ToDo:
# - Create some variables for regular expressions that are used multiple
#   times.
# - Currently, '&' signs at the endings of lines are not recognized as
#   continued line when parsing free-form code.
# - Check if statement checks for indentation are complete.
# - Check if 'where' statements are matched correctly.
# - Operator matching usually does not work at beginnings or endings
#   of parts.
# - CodeStatement for (cont.) statement identification
#
# created by Florian Zwicke, Feb. 10, 2016
#########################################################################

import sys
import re

#########################################################################
# Class for source code representation                                  #
#########################################################################
class CodeFile:
  """Class that represents a Fortran source code file"""

  #######################################################################
  # Function to read the source code from a file                        #
  #######################################################################
  def __init__(self, fileName, isFreeForm, hint=""):
    # try to open file
    with open(fileName) as file:
      content = file.readlines()

    # do initializations
    self.codeLines = []
    self.hint = hint

    # go through lines and parse
    for line in content:
      self.codeLines.append(CodeLine(line, isFreeForm, hint))

  #######################################################################
  # Function to fix the indentation                                     #
  #                                                                     #
  # (This only makes sense in free-form code.)                          #
  # (Continuations must be known.)                                      #
  #######################################################################
  def fixIndentation(self, indent, contiIndent):
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

    # back at zero indentation?
    if curIndent > 0:
      self.codeLines[-1].remarks.append("Positive indentation level remaining.")

  #######################################################################
  # Function to check line length                                       #
  #                                                                     #
  # (This must be called right at the end.)                             #
  #######################################################################
  def markLongLines(self, allowedLength):
    for codeLine in self.codeLines:
      if codeLine.getLength() > allowedLength:
        codeLine.remarks.append("Line above is longer than " + str(allowedLength) \
            + " characters.")

  #######################################################################
  # Look for old-style Doxygen blocks and transform them                #
  #                                                                     #
  # (This must be called after parsing and converting to free-form.)    #
  #######################################################################
  def transformDoxygenBlocks(self, length):
    inBlock = False
    for codeLine in self.codeLines:
      if codeLine.comment.count("c") == 70:
        inBlock = not inBlock
        codeLine.comment = "!" + "-" * (length - 1)
        continue

      if inBlock:
        # is it many dashes?
        if codeLine.comment.count("-") == 60:
          codeLine.comment = "!>"
          continue

        # is it the filename?
        match = re.match(r"!\s(\S+\.\S+)\s+c$", codeLine.comment)
        if match:
          codeLine.comment = "!> @file " + match.group(1)
          continue

        # is it a param?
        match = re.match(r"!\s>\s+\\(param.*?)$", codeLine.comment)
        if match:
          codeLine.comment = "!> @" + match.group(1)
          continue

        # is it a date?
        match = re.match(r"!\s(\d{4}\.\d{2}\.\d{2})\s-\s(.*?)\s+c$", codeLine.comment)
        if match:
          codeLine.comment = "!> @date " + match.group(1) + " -- " + match.group(2)
          continue

        # is it a mail address?
        match = re.match(r"!\s(.*?)\s\[(.*?@.*?\..*?)\]\s+c$", codeLine.comment)
        if match:
          codeLine.comment = "!> @authors " + match.group(1) + " <" + match.group(2) + ">"
          continue

        # or is it the description?
        codeLine.comment = "!> @brief " + codeLine.comment[3:].lstrip()

  #######################################################################
  # Function to search for continuations                                #
  #                                                                     #
  # (This must be called after parsing but before stripping             #
  #  whitespaces at end and fixing indentation.)                        #
  #######################################################################
  def identifyContinuations(self):
    # go through lines in reverse order
    inConti = False
    inTightConti = False
    for codeLine in reversed(self.codeLines):
      # is it a code line and is it followed by continuation?
      if codeLine.hasCode() and inConti:
        codeLine.isContinued = True
        # is it a 'tight' continuation?
        if inTightConti and not len(codeLine.midSpace) \
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

  #######################################################################
  # Function to rebuild the source code from the lines                  #
  #######################################################################
  def rebuild(self):
    output = ""

    for codeLine in self.codeLines:
      output += codeLine.rebuild()

    return output


#########################################################################
# Class for source code representation                                  #
#########################################################################
class CodeLine:
  """Class that represents a Fortran source code line"""

  #######################################################################
  # Function to parse one line of source code                           #
  #######################################################################
  def __init__(self, line, isFreeForm, hint):
    # initializations
    self.isFreeForm = isFreeForm
    self.remarks = []
    self.line = line
    self.origCodeLength = 0
    self.hint = hint

    # line parts
    self.preProc = ""
    self.leftSpace = ""
    self.code = ""
    self.midSpace = ""
    self.comment = ""
    self.rightSpace = ""

    # line parts in fixed-form
    self.fixedComment = ""
    self.fixedLabel = ""
    self.fixedCont = ""

    # line parts in free-form
    self.freeLabel = ""
    self.freeContBeg = ""
    self.freeContEnd = ""

    # line properties
    self.isContinued = False
    self.isContinuation = False
    self.isTightContinued = False
    self.isTightContinuation = False

  #######################################################################
  # Remove all tabs from line and replace by right amount of spaces     #
  #                                                                     #
  # (This function must be called BEFORE parsing.)                      #
  #######################################################################
  def replaceTabs(self, tabLength):
    # As long as the line contains tabs, find the first one ...
    tabPos = self.line.find("\t")
    while tabPos != -1:
      # ... and replace it with spaces.
      spaces = " " * (tabLength - tabPos % tabLength)
      self.line = self.line[:tabPos] + spaces + self.line[tabPos+1:]

      # Then find next one.
      tabPos = self.line.find("\t")

  #######################################################################
  # Parse the different parts of the line                               #
  #######################################################################
  def parseLine(self):
    # first strip away any trailing whitespace
    match = re.match(r"(.*?)(\s+)$", self.line)
    if match:
      self.rightSpace = match.group(2)
      self.line = match.group(1)

    # ignore empty lines
    if not len(self.line):
      return

    # check for preprocessor lines
    if self.line[0] == '#':
      self.preProc = self.line
      return

    # some fixed-form checks
    if not self.isFreeForm:
      # check for comment symbol in first column
      if self.line[0] in ['c', 'C', '*', '!']:
        self.fixedComment = self.line
        return

      # check for label
      match = re.match(r"\s{0,4}(\d+)(.*?)$", self.line)
      if match:
        self.fixedLabel = match.group(1)
        self.line = match.group(2)
      # otherwise check for continuation
      elif len(self.line) > 5 and self.line[0] != "\t" and self.line[5] not in [' ', '0']:
        self.fixedCont = self.line[:6]
        self.isContinuation = True
        self.line = self.line[6:]

    # strip away left whitespace
    match = re.match(r"(\s+)(.*?)$", self.line)
    if match:
      self.leftSpace = match.group(1)
      self.line = match.group(2)

    # check for free comments
    match = re.match(r"((?:[^!'\"]|\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')*?)(\s*)(!.*?)$", \
        self.line)
    if match:
      self.midSpace = match.group(2)
      self.comment = match.group(3)
      self.line = match.group(1)

    # free-form checks
    if self.isFreeForm:
      # check for free label
      match = re.match(r"(\d+\s+)(.*?)$", self.line)
      if match:
        self.freeLabel = match.group(1)
        self.line = match.group(2)

      # check for continuation
      match = re.match(r"(&\s*)(.*?)$", self.line)
      if match:
        self.freeContBeg = match.group(1)
        self.isContinuation = True
        self.line = match.group(2)

    # finished
    self.code = self.line
    self.line = ""

    # record length of code in this line
    self.origCodeLength = len(self.code)

  #######################################################################
  # Check if line has code                                              #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def hasCode(self):
    if len(self.code):
      return True
    else:
      return False

  #######################################################################
  # Remove whitespace on the right side                                 #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def stripTrailingWhitespace(self):
    self.rightSpace = "\n"

  #######################################################################
  # Convert a line from fixed-form to free-form                         #
  #                                                                     #
  # (This function requires that continuations have been identified.)   #
  #######################################################################
  def convertFixedToFree(self):
    if self.isFreeForm:
      return
    self.isFreeForm = True

    # convert comments
    if len(self.fixedComment):
      if len(self.fixedComment[1:].lstrip()):
        self.comment = "! " + self.fixedComment[1:].lstrip()
      self.fixedComment = ""
      return

    # label
    if len(self.fixedLabel):
      self.freeLabel = self.fixedLabel + " "
      self.fixedLabel = ""

    # continuation
    if len(self.fixedCont):
      # need double check in case there is no code
      if self.isContinuation:
        self.freeContBeg = "&" if self.isTightContinuation else "& "
      self.fixedCont = ""

    # continued line?
    if self.isContinued:
      self.freeContEnd = "&" if self.isTightContinued else " &"

  #######################################################################
  # Prescribe an indentation for the line                               #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  # (This only makes sense in free-form.)                               #
  #######################################################################
  def setIndentation(self, level, indent):
    if self.hasCode() or len(self.comment):
      self.leftSpace = indent * level
    else:
      self.leftSpace = ""

  #######################################################################
  # Fix variable declarations                                           #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def fixDeclarationsInCode(self):
    # 'real*8' to 'real(RK)'
    self.code = re.sub(r"(?i)^\breal\b\s?\*\s?(\d+)\b", r"real(\1)", self.code)
    #self.code = re.sub(r"(?i)^\breal\b\s?\*\s?8\b", r"real(RK)", self.code)

  #######################################################################
  # Add spaces around operators and after commas                        #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def addSpacesInCode(self):
    # mark non-escaped quotation marks by an 'a' in front (this is arbitrary)
    marked = re.sub(r"([^\\]|^)(\")", r"\1a\2", self.code)
    # now split by 'a"'
    parts = re.split(r"a\"", marked)
    # now you can go through all even-numbered parts
    for i in range(0, len(parts), 2):
      part = parts[i]

      ## commas
      #part = re.sub(r",(\S)", r", \1", part)

      ## operator /
      #if part.find("common") == -1:
      #  part = re.sub(r"(/)(\S)", r"\1 \2", part)
      #  part = re.sub(r"(\S)(/)", r"\1 \2", part)

      ## operator * (only if it's not **)
      #part = re.sub(r"((?:[^\*]|^)\*)([^\s\*])", r"\1 \2", part)
      #part = re.sub(r"([^\s\*])(\*(?:[^\*]|$))", r"\1 \2", part)

      ## operator -
      #part = re.sub(r"(-)(\S)", r"\1 \2", part)
      #part = re.sub(r"(\S)(-)", r"\1 \2", part)

      ## operator +
      #part = re.sub(r"(\+)(\S)", r"\1 \2", part)
      #part = re.sub(r"(\S)(\+)", r"\1 \2", part)

      ## operator =
      #part = re.sub(r"(=)(\S)", r"\1 \2", part)
      #part = re.sub(r"(\S)(=)", r"\1 \2", part)

      # after 'if', 'where'
      part = re.sub(r"(?i)\b(if|where)\(", r"\1 (", part)
      # before 'then'
      part = re.sub(r"(?i)\)then\b", r") then", part)

      # 'endif', 'enddo', 'endwhile' -> 'end if', ...
      part = re.sub(r"(?i)\bend(if|do|while)\b", r"end \1", part)
      # 'elseif' -> 'else if'
      part = re.sub(r"(?i)\belseif\b", r"else if", part)
      # 'inout' -> 'in out'
      part = re.sub(r"(?i)\binout\b", r"in out", part)

      # '.eq.', ...
      #part = re.sub(r"(?i)(\S)(\.(?:eq|ne|lt|gt|le|ge|and|or)\.)", r"\1 \2", part)
      #part = re.sub(r"(?i)(\.(?:eq|ne|lt|gt|le|ge|and|or)\.)(\S)", r"\1 \2", part)

      parts[i] = part

    # put parts back together
    self.code = "\"".join(parts)

  #######################################################################
  # Find out if this line increases the indentation afterwards          #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def increasesIndentAfter(self):
        #or re.match(r"(?i)(\w+:\s*)?if\b.*?\bthen\b", self.code) \
    if re.match(r"(?i)(\w+:\s*)?do\b", self.code) \
        or re.search(r"(?i)\bthen$", self.code) \
        or re.match(r"(?i)program\b", self.code) \
        or re.match(r"(?i)subroutine\b", self.code) \
        or re.match(r"(?i)module\b", self.code) \
        or re.match(r"(?i)type\s*[^\s\(]", self.code) \
        or re.match(r"(?i)interface\b", self.code) \
        or re.match(r"(?i)block\s?data\b", self.code) \
        or re.match(r"(?i)function\b", self.code) \
        or re.match(r"(?i)select\b", self.code) \
        or re.match(r"(?i)case\b", self.code) \
        or re.match(r"(?i)else$", self.code):
        #or re.match(r"(?i)else(if)?\b", self.code):
      return True
    else:
      # need to check for where statement separately
      if re.match(r"(?i)where\b", self.code):
        trans = self.code

        # remove double quoted strings
        trans = re.sub(r"\"([^\"\\]|\\.)*\"", r"str", trans)
        # remove single quoted strings
        trans = re.sub(r"'([^'\\]|\\.)*'", r"str", trans)

        # now keep replacing innermost brackets using '!'
        # (! cannot occur outside of strings)
        while re.search(r"\([^\(\)]+\)", trans):
          trans = re.sub(r"\([^\(\)]+\)", "!", trans)

        # now if just one '!' remains, there was only one
        # bracket term
        if trans.count("!") == 1:
          return True

      return False

  #######################################################################
  # Find out if this line decreases the indentation before              #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def decreasesIndentBefore(self):
    if re.match(r"(?i)(end(if|do|where)?|else(if)?)\b", self.code) \
        or re.match(r"(?i)case\b", self.code):
      return True
    else:
      return False

  #######################################################################
  # Unindent preprocessor commands                                      #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def unindentPreProc(self):
    if len(self.preProc):
      self.preProc = "#" + self.preProc[1:].lstrip()

  #######################################################################
  # Function to make sure that continuation actually contains code      #
  #                                                                     #
  # (This function must be called after parsing and before              #
  #  continuations are identified.)                                     #
  #######################################################################
  def verifyContinuation(self):
    if not self.hasCode():
      self.isContinuation = False


  #######################################################################
  # Swallow up length changes in space between code and comment         #
  #                                                                     #
  # (This function must be called after all code changes.)              #
  #######################################################################
  def swallowLengthChange(self):
    # if there is no comment, just return because there is no space to
    # change
    if not len(self.comment) or not self.hasCode():
      return

    lengthChange = len(self.code) - self.origCodeLength
    # no change for no length change
    if not lengthChange:
      return
    # at least one space must remain
    numLeftSpaces = max(1, len(self.midSpace) - lengthChange)
    self.midSpace = " " * numLeftSpaces

  #######################################################################
  # Rebuild line from parsed info                                       #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def buildFullLine(self):
    return self.preProc + self.fixedComment + self.fixedLabel + self.fixedCont\
           + self.leftSpace + self.freeLabel + self.freeContBeg + self.code\
           + self.freeContEnd + self.midSpace + self.comment \
           + self.rightSpace

  #######################################################################
  # Return line length                                                  #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def getLength(self):
    return len(self.buildFullLine()) - 1 # ignore line break

  #######################################################################
  # Rebuild line including remarks                                      #
  #                                                                     #
  # (This function must be called after parsing.)                       #
  #######################################################################
  def rebuild(self):
    output = self.buildFullLine()
    for remark in self.remarks:
      output += "! " + self.hint + ": " + remark + "\n"
    return output
