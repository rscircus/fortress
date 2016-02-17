FORTRAN CodeCleaner and Linter

Cleans archaic Fortran code.

## Features:

* Convert fixed form code to free form code
* Tab -> Space conversion
* Add spaces around/behind operators and typical structures
* Strip trailing whitespace
* Clean up Doxygen headers
* Lint using `gfortran` as backend


## Usage:

```
./convertFile.py file1.F file2.F ... fileN.F
./convertFile.py *.F
```

## Changelog:

### 2016.02.17
Added:
- README.md

Added:
- Import original project from Florian Z's repo.


## Genesis Note:

This started out while scratching our own itches.
