__date__    = "$Date: 2016/02/17 $"
__license__ = "MIT" # Flo?
__author__ = "Roland Siegbert <r@rscircus.org>"

import subprocess
import re

class codelinter:
  """Use gfortran as linter"""
  def __init__(self, fileName):

    self.linter = "gfortran"
    self.fileName = fileName

  def lint(self):
    p = subprocess.Popen([self.linter,
                          '-fsyntax-only',  # perform syntax checks only
                          '-Wall',          # print all warnings
                          '-Wextra',
                          self.fileName],
                          stdout = subprocess.PIPE,
                          stderr = subprocess.PIPE,
                          stdin  = subprocess.PIPE)

    # adding group names in Python style here => better identification
    catchRe = "(.+):(?P<line>\\d+):(?P<col>\\d+):((.|\\n)*)(?P<type>(Error|Warning|Note)):\\s*(?P<message>.*)"

    # execute linter:
    stdOut, stdErr = p.communicate()
    caughtIter = re.finditer(catchRe, stdErr)

    # print errors:
    for el in caughtIter:
      print "Line:      " + el.group('line')
      print "Column:    " + el.group('col')
      print "Errortype: " + el.group('type')
      print "Message:   " + el.group('message')
