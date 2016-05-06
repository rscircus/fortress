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

def CreateFortran2003Style():
  return dict(
    INDENT_WIDTH=4,
    CONTI_INDENT_WIDTH=4,
    UNINDENT_PREPROCESSOR_DIRECTIVES=True,
    REPLACE_TABS_BY_SPACES=True,
    CONVERT_FIXED_TO_FREE=False,
    ADD_SPACES_AROUND_OPERATORS=False,
    FIX_LINE_ENDINGS=True,
    ADD_REMARKS=False,
    REINDENT=False
  )

def CreateStrictStyle():
  return dict(
    INDENT_WIDTH=4,
    CONTI_INDENT_WIDTH=4,
    UNINDENT_PREPROCESSOR_DIRECTIVES=True,
    REPLACE_TABS_BY_SPACES=True,
    CONVERT_FIXED_TO_FREE=False,
    ADD_SPACES_AROUND_OPERATORS=True,
    FIX_LINE_ENDINGS=True,
    ADD_REMARKS=False,
    REINDENT=True
  )

def CreateStyleFromConfig(config_filename):
  """Read the style.ini and return style based on Fortran2003 std."""

  # Initialize base style:
  style = CreateStrictStyle()

  # Provide meaningful error here.
  if not os.path.exists(config_filename):
    return style

  with open(config_filename) as style_file:
    config = py3compat.ConfigParser()
    config.read_file(style_file)

# TODO: Error handling
    if config_filename.endswith(BASIC_STYLE):
      if not config.has_section('style'):
        return None
    elif config_filename.endswith(DIR_STYLE):
      if not config.has_section('style'):
        return None
    else:
      if not config.has_section('style'):
        return None
  
  # Load options into style
  # TODO: Error handling - i.e. typos, type mismatch
  for option, value in config.items('style'):
    option = option.upper()
    style[option] = _STYLE_CONVERTER[option](value)

  return style

# Sets the default style
BASIC_STYLE = 'style.ini'

# TODO: Varies based on directory
DIR_STYLE = '.style.ini'

def _BoolConverter(s):
  """Converter for booleans"""
  return py3compat.CONFIGPARSER_BOOLEAN_STATES[s.lower()]

_STYLE_CONVERTER = dict(
  INDENT_WIDTH=int,
  CONTI_INDENT_WIDTH=int,
  UNINDENT_PREPROCESSOR_DIRECTIVES=_BoolConverter,
  REPLACE_TABS_BY_SPACES=_BoolConverter,
  CONVERT_FIXED_TO_FREE=_BoolConverter,
  ADD_SPACES_AROUND_OPERATORS=_BoolConverter,
  FIX_LINE_ENDINGS=_BoolConverter,
  ADD_REMARKS=_BoolConverter,
  REINDENT=_BoolConverter
)

_style = {}
