# uCal

The uCal module is a Python-based calculator which seamlessly integrates unit conversion.

### Status
[![Build Status](https://travis-ci.org/timkostka/ucal.png)](https://travis-ci.org/timkostka/ucal)


## Method of operation

The uCal engine evaluates an expression using the folowing steps.
* Tokenizing


### Tokenizing

Starting with a string expression, the string is broken up into substring, each of which represents a token.  The following tokens are possible.
* Value
  * This is a number.  Valid strings are `1`, `1e67`, `+1`, `-32.1E+526`, etc.
* Variable
  * This is text such as `mm`, `kg`, etc.
* Function
  * A function follows the same rules as a variable, but is immediately followed by an opening parenthesis token.
* Opening parenthesis
  * This is the `(` sign.
* Closing parenthesis
  * This is the `)` sign.
* Prefix operator
  * This operates on the value immediately following it, such as the first `-` in `3 - -7`.
  * Valid operators of this type are `+` and `-`.
* Infix operator
  * An infix operator is an operator that operates on the value before and after it, such as `+` for addition.
  * Valid operators of this type are `+`, `-`, `*`, `/`, `^` for exponentiation, and `%` for modulo operation.
* Postfix operator
  * A postfix operator operates on the value immediately preceeding it.
  * The only valid operator of this type is the factorial operator `!`.


### Interpret the percent sign

The percent sign `%` can be either the modulo operator or a percentage.  We interpret it by looking at its context and determining which makes sense.

It is interpreted as a percentage if the previous token is a value and either it is the last token in the expression, or the next token is an infix operator or an opening parenthesis.

Examples where it would be interpreted as the modulo operator are `1 % 2`.

Examples where it would be interpreted as a percentage are `30%`, and `80% - 10%`.

Percentages are effectively replaced with `*(0.01)`  For example, `30%` becomes `30*(0.01)`. 

### Interpret implicit multiplication

Implicit multiplication is added between tokens as appropriate.  There are a limited number of instances in which multiplication is implies.  These are the following.

* Between a value and a variable or function.
  * Example: `1 in` is interpreted as `1 * in`.
* Between a variable and a variable or function.
  * Example: `in lbs` is interpreted as `in * lbs`.
* Between a closing parenthesis and an opening parenthsis.
  * Example: `(1) (2)` is interpreted as `(1) * (2)`.


### Check syntax

The string of tokens is then checked for make sure the syntax makes sense.

* Check for balanced parenthesis
* Check prefix operators are followed by a quantity.
* Check infix operators are preceeded and followed by a quantity.
* Check postfix operators are preceeded by a quantity.
* Check starting token is either a prefix operator or a quantity.
* Check ending token is either a postfix operator or a quantity.
