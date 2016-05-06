# FORTRAN CodeCleaner and Linter

Cleans archaic Fortran code.


## Features:

* Convert fixed form code to free form code
* Tab -> Space conversion
* Add spaces around/behind operators and typical structures
* Strip trailing whitespace
* Easily pluggable (vim-plugin inside)


## Planned Features:

* Lint using `gfortran` as backend


## Installation:

On your local machine, this should work:

```
python setup.py install
```

Working on a cluster or remote without any rights, a more fine grained approach:

```
python setup.py install --user --record install.txt
```


## Usage:

```
> fortress -h
usage: fortress [-h] [-v] [-d | -i] [-r | -l START-END] [-e PATTERN] [-t]
                [files [files ...]]

FORTRESS is a formatter/modernizer of legacy FORTRAN code.
----------------------------------------------------------

  By default it prints the reformatted code
  to STDOUT. For other options see below.

positional arguments:
  files

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show version
  -d, --diff            print the diff for the fixed source
  -i, --in-place        make changes to files in place
  -r, --recursive       run recursively over dirs
  -l START-END, --lines START-END
                        range of lines to reformat; 1-based
  -e PATTERN, --exclude PATTERN
                        patterns for files to exclude from formatting
  -t, --lint            lint files
```


## Changelog:

### 2016.05.02

Added:
- Add new frontend
- Add Vim plugin

Removed:
- Old frontend

### 2016.02.17
Changed:
- Structure. Everything in `./src` now.

Added:
- README.md
- TODO.md

Imported:
- Import original project from Florian Z's repo.


## Genesis Note:

This started out while scratching our own itches.
