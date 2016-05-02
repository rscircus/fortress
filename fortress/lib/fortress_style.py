"""FORTRAN formatting style settings."""

import os
import re
import textwrap

#from fortress.lib import errors
from fortress.lib import py3compat

def Get(setting_name):
  """Get a style setting."""
  return _style[setting_name]

def SetGlobalStyle(style):
  """Set a style dict."""
  global _style
  _style = style

# Fortran 2003 Style
def CreateSaneStyle():
  return dict(
    INDENT_WIDTH=4,
    CONTI_INDENT_WIDTH=4,
    UNINDENT_PREPROCESSOR_DIRECTIVES=True,
    REPLACE_TABS_BY_SPACES=True,
    CONVERT_FIXED_TO_FREE=True,
    READABLE_PARENTHESES=True,
  )

# And CATS :-D
def CreateCatsStyle():
  style = CreateSaneStyle()
  style['INDENT_WIDTH'] = 8
  return style


_style = {}
