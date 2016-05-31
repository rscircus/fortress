__date__    = "$Date: 2016/02/17 $"
__license__ = "MIT" # Flo?
__authors__ = [
    "Florian Zwicke <z@zwicke.org>",
    "Roland Siegbert <r@rscircus.org>"
    ]

import re

class UnwrappedLine:
  """Class that represents a Fortran source code line"""

  def __init__(self, line, isFreeForm):
    # initializations
    self.isFreeForm = isFreeForm # TODO: Remove as this can be checked
    self.remarks = []
    self.origLine = line
    self.origCodeLength = 0

    self.line = line
    self.lineNo = -1
    self.enabled = True

    # line parts
    self.preProc = ""
    self.leftSpace = ""
    self.code = ""
    self.commentSpace = ""
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

  def replaceTabsBySpaces(self, tabLength):
    """Remove all tabs from line and replace by right amount of spaces.

    Note:
      Call BEFORE parsing.

    """
    # As long as the line contains tabs, find the first one ...
    tabPos = self.line.find("\t")
    while tabPos != -1:
      # ... and replace it with spaces.
      spaces = " " * (tabLength - tabPos % tabLength)
      self.line = self.line[:tabPos] + spaces + self.line[tabPos+1:]

      # Then find next one.
      tabPos = self.line.find("\t")

  def tokenize(self):
    """Tokenizes a line and performs various checks.

    Note:
      The line is modified already by stripping away leading and trailing spaces.

    """
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
      #elif len(self.line) > 5 and self.line[0] != "\t" and self.line[5] not in [' ', '0']:
      elif len(self.line) > 5 and self.line[5] == "&":
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
      self.commentSpace = match.group(2)
      self.comment = match.group(3)
      self.line = match.group(1)

    # free-form checks
    if self.isFreeForm:
      # check for free label
      match = re.match(r"(\d+\s+)(.*?)$", self.line)
      if match:
        self.freeLabel = match.group(1)
        self.line = match.group(2)

      # TODO: tight (no spaces) freeContXXX > 1
      # check for continuation start
      match = re.match(r"(&\s*)(.*?)$", self.line)
      if match:
        self.freeContBeg = match.group(1)
        self.isContinuation = True
        self.line = match.group(2)
        # tight?
        if len(self.freeContBeg) == 1:
          self.isTightContinuation = True

      # check for continuation end
      match = re.match(r"(.*?)(\s*&)$", self.line)
      if match:
        self.freeContEnd = match.group(2)
        self.isContinued = True
        self.line = match.group(1)
        # tight?
        if len(self.freeContEnd) == 1:
          self.isTightContinued = True

    # finished
    self.code = self.line
    self.line = ""

    # record length of code in this line
    self.origCodeLength = len(self.code)

  def hasCode(self):
    """Returns true if line has code."""
    if len(self.code):
      return True
    else:
      return False

  def convertFixedToFree(self):
    """Convert from fixed-form to free-form.

    Note:
      Continuations have be identified prior to this.

    """
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

  def setIndentation(self, level, indent):
    """Set correct multiple of indent to current line."""
    if self.hasCode() or len(self.comment):
      self.leftSpace = indent * level
    else:
      self.leftSpace = ""

  def fixDeclarationsInCode(self):
    """Replaces real*8 with real(RK)"""
    # 'real*8' to 'real(RK)'
    self.code = re.sub(r"(?i)^\breal\b\s?\*\s?(\d+)\b", r"real(\1)", self.code)
    #self.code = re.sub(r"(?i)^\breal\b\s?\*\s?8\b", r"real(RK)", self.code)

  def fixFreeContinuation(self):
    """Add ampersands at beginnings of continued lines"""

    if self.isContinuation and len(self.freeContBeg) == 0:
      self.freeContBeg = ("&" + self.leftSpace) if self.isTightContinuation else "& "


  def addSpacesInCode(self):
    """Enhances readability by adding spaces between various operators."""
    # mark non-escaped quotation marks by an 'a' in front (this is arbitrary)
    marked = re.sub(r"([^\\]|^)(\")", r"\1a\2", self.code)
    # now split by 'a"'
    parts = re.split(r"a\"", marked)
    # now you can go through all even-numbered parts
    for i in range(0, len(parts), 2):
      part = parts[i]

      ## commas
      part = re.sub(r",(\S)", r", \1", part)

      ## operator /
      if part.find("common") == -1:
        part = re.sub(r"(/)(\S)", r"\1 \2", part)
        part = re.sub(r"(\S)(/)", r"\1 \2", part)

      ## operator * (only if it's not **)
      part = re.sub(r"((?:[^\*]|^)\*)([^\s\*])", r"\1 \2", part)
      part = re.sub(r"([^\s\*])(\*(?:[^\*]|$))", r"\1 \2", part)

      ## operator -
      part = re.sub(r"(-)(\S)", r"\1 \2", part)
      part = re.sub(r"(\S)(-)", r"\1 \2", part)

      ## operator +
      part = re.sub(r"(\+)(\S)", r"\1 \2", part)
      part = re.sub(r"(\S)(\+)", r"\1 \2", part)

      ## operator =
      part = re.sub(r"(=)(\S)", r"\1 \2", part)
      part = re.sub(r"(\S)(=)", r"\1 \2", part)

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
# TODO: Replace with 'modern' rel. op.

      parts[i] = part

    # put parts back together
    self.code = "\"".join(parts)

  def increasesIndentAfter(self):
    """Identify level increasing indentation manipulators."""
    trans = self.code

    # remove double quoted strings
    trans = re.sub(r"\"([^\"\\]|\\.)*\"", r"str", trans)
    # remove single quoted strings
    trans = re.sub(r"'([^'\\]|\\.)*'", r"str", trans)

        #or re.match(r"(?i)(\w+:\s*)?if\b.*?\bthen\b", self.code) \
    if re.match(r"(?i)(\w+:\s*)?do\b", trans) \
        or re.search(r"(?i)\bthen$", trans) \
        or re.match(r"(?i)program\b", trans) \
        or re.match(r"(?i)subroutine\b", trans) \
        or re.match(r"(?i)module\b", trans) \
        or re.match(r"(?i)type\s*[^\s\(]", trans) \
        or re.match(r"(?i)interface\b", trans) \
        or re.match(r"(?i)block\s?data\b", trans) \
        or re.search(r"(?i)\bfunction\b", trans) \
        and not re.match(r"(?i)end\b", trans) \
        or re.match(r"(?i)select\b", trans) \
        or re.match(r"(?i)case\b", trans) \
        or re.match(r"(?i)else$", trans):
        #or re.match(r"(?i)else(if)?\b", self.code):
      return True
    else:
      # need to check for where statement separately
      if re.match(r"(?i)where\b", trans):

        # now keep replacing innermost brackets using '!'
        # (! cannot occur outside of strings)
        while re.search(r"\([^\(\)]+\)", trans):
          trans = re.sub(r"\([^\(\)]+\)", "!", trans)

        # now if just one '!' remains, there was only one
        # bracket term
        if trans.count("!") == 1:
          return True

      return False

  def decreasesIndentBefore(self):
    """Identify level decreasing indentation manipulators."""
    if re.match(r"(?i)(end(if|do|where)?|else(if)?)\b", self.code) \
        or re.match(r"(?i)case\b", self.code):
      return True
    else:
      return False

  def unindentPreProc(self):
    """Unindent preprocessor commands."""
    if len(self.preProc):
      self.preProc = "#" + self.preProc[1:].lstrip()

  def preserveCommentPosition(self):
    """Move comment to same position after indentation changes."""
    # if there is no comment, just return because there is no space to
    # change
    if not len(self.comment) or not self.hasCode():
      return

    lengthChange = len(self.code) - self.origCodeLength

    # no change for no length change
    if not lengthChange:
      return

    # at least one space must remain
    numLeftSpaces = max(1, len(self.commentSpace) - lengthChange)
    self.commentSpace = " " * numLeftSpaces

  def buildFullLine(self):
    """Returns string via CodeLine after all changes were performed."""
    return self.preProc + self.fixedComment + self.fixedLabel + self.fixedCont\
           + self.leftSpace + self.freeLabel + self.freeContBeg + self.code\
           + self.freeContEnd + self.commentSpace + self.comment \
           + self.rightSpace

  def getLength(self):
    """Returns length of built line."""
    return len(self.buildFullLine()) - 1 # ignore line break

  def rebuild(self):
    """Returns file as string built from all CodeLines."""
    output = self.buildFullLine()
    for remark in self.remarks:
      output += "! REMARK: " + remark + "\n"
    return output
