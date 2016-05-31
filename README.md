# FORTRAN CodeCleaner and Linter

Cleans archaic Fortran code.


## Installation and Simple Use Case.

[![](https://asciinema.org/a/47055.png)](https://asciinema.org/a/47055)


## Features:

* Convert fixed form code to free form code
* Tab -> Space conversion
* Add spaces around/behind operators and typical structures
* Strip trailing whitespace
* Easily pluggable (vim-plugin inside)


## Planned Features:

* Lint using `gfortran` as backend


## Installation:

Assuming, you cloned the repo into your location of choice via:

```
git clone https://github.com/rscircus/fortress
cd fortress
```

On your local machine, this should work:
```
python setup.py install
```

Working on a cluster or remote without any rights, a more fine grained approach:
```
python setup.py install --user
```

If you want to deinstall FORTRESS later on, you can use 
```
python setup.py install --user --record install.txt
```
instead. All installed files are documented in `install.txt` then.

Furthermore the installation dir should be added to `PATH`. I.e.:
```
export PATH=$PATH:~/.local/bin
```


## Usage:

```
> fortress -h
usage: fortress [-h] [-v] [-d | -i] [-r | -l START-END] [-e PATTERN]
                [-s STYLE] [--strict] [-t]
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
  -s STYLE, --style STYLE
                        specify formatting style via local style.ini
  --strict              applies all available formatting options / style.ini
                        will be ignored
  -t, --lint            lint files
```


## Genesis Note:

This started out while scratching our own itches.
