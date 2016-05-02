# TODO
  * Clean up line endings: convert any '\r\n' or '\r' to '\n'
  * Attach filter structure
  * Generalize codeline

## src/codefile.py

```
261:# TODO: tight (no spaces) freeContXXX > 1
391:# TODO: Replace with 'modern' rel. op.
```

## fixFreeForm.py
```
23:# TODO: Shift into CodeFile, s.t. codeLine can be arbitrary
25:# TODO: Identify and automate Fixed vs. Free
```

# From previous codefile.py (now reformatter.py)
  * Create some variables for regular expressions that are used multiple
    times.
  * Currently, '&' signs at the endings of lines are not recognized as
    continued line when parsing free-form code.
  * Check if statement checks for indentation are complete.
  * Check if 'where' statements are matched correctly.
  * Operator matching usually does not work at beginnings or endings
    of parts.
  * CodeStatement for (cont.) statement identification
  * Split codeline into FreeLine and FixedLine
  * Statements only in Free (after conversion)
  * Move parseLine into constructor - DONE: 2016-02-16 Tue 10:30 @roland
  * Reinsert execution position for functions (PARSE LINE?) @roland
  * Note that the ampersand at the beginning of lines is optional
  * in free-form. This is currently not supported by this script.
