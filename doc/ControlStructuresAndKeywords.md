# Basic Control Structures in Fortran 90:

Remarks and important hints with focus on minimally viable examples up to FORTRAN 90.

Sources:

* http://www.augustana.ca/~mohrj/courses/common/csc370/lecture_notes/fortran.html
* https://en.wikibooks.org/wiki/Fortran/Fortran_control
* http://www.cs.mtu.edu/~shene/COURSES/cs201/NOTES/F90-Control.pdf
* http://www.obliquity.com/computer/fortran

By Roland Siegbert (siegbert@cats.rwth-aachen.de)

## Versions of Fortran:

```
1954    FORTRAN I     - specified
1956    FORTRAN I     - implemented for the IBM 704
1958    FORTRAN II
1958    FORTRAN III
1962    FORTRAN IV    - still an important dialect
1966    ANS FORTRAN   - ANSI standard FORTRAN IV (2 versions)
1977    FORTRAN 77
1990    FORTRAN 90    <--- This document covers FORTRAN until here
1997    FORTRAN 95
2004    FORTRAN 2003
2010    FORTRAN 2008
????    FORTRAN 2015
```

## Syntactic Structure:

### Fixed Format:


| Columns | Purpose          |
|---------|------------------|
| 1 - 5   | statement number |
| 6       | continuation     |
| 7 - 72  | statement        |
| 73 - 80 | sequence number  |



## Branching:

### if: (can be labelled)

```
if (logical expression1)       then
    ''Lines of Fortran''
 else if (logical expression2) then
    ''Lines of Fortran''
 else if (logical expression3) then
    ''Lines of Fortran''
 else
    ''Lines of Fortran''
 end if
```

Beware of these archaic forms:

```
if (''logicalExpression'') {GO TO, GOTO} ''lineNumber''
if (''arithmeticExpression'') ''firstLineNumber'', ''secondLineNumber'', ''thirdLineNumber''
if (''logicalExpression'') statement
```

In the first form, things are pretty straightforward. In the second form, the arithmetic expression is evaluated. If the expression evaluates to a negative number, then execution continues at the first line number. If the expression evaluates to zero, then execution continues at the second line number. Otherwise, execution continues at the third line number. In the last example the statement will only be evaluated if logicalExpression evaluates to .true. .

### select case:

```
select case (month)
    case ("January")
       num_days = 31
    case ("February")
       num_days = 28
       print *,"You can put more stuff here."
    case ("March")
       num_days = 31
    case default
       num_days = 30
end select
```


## Loops:

### do:

```
do i=1,10
    ''Lines of Fortran''
end do
```

```
      DO label, loop-control-variable = initial-value, final-value, step-size
         statement1
         statement2
…
         statementn
label CONTINUE
```

### do-while loop: (labelled)

```
10    IF (Z .GE. 0D0) THEN
         Z = Z - SQRT(Z)
         GO TO 10
      END IF
```


### repeat-until loop: (labelled)

```
label CONTINUE
         statements
      IF (logical-expression) GO TO label
```

## Simple Statements:

`GO TO`, `GOTO`
`STOP conditionCode` - will stop if conditionCode. `STOP 0` is often evaluated as failure.
`EXIT` - leave loop
`CONTINUE` - end current loop in `do` loop (can be labelled)
`CYCLE` - end `do` at `end do`
`RETURN` - leaves subroutine or function
`PAUSE` -
`READ n, list`
`PUNCH n, list`
