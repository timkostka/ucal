"""
The ucal module evaluates expressions with automatic unit conversions.

Typically, this module is used from ucal_gui.py to perform calculations,
however it can also be used as a standalone module.

Usage:

import ucal
>>> ucal.evaluate("5km in mi")
'3.10686 mi'
>>> ucal.evaluate("sqrt(2 * g * 30ft) in fps")
'43.9367 fps'
>>> ucal.evaluate("5V * 500mA")
'2.5 W'
>>> ucal.evaluate("1mi + 10km")
'11609.344 m'

"""

import inspect
import textwrap
import math
import decimal
import string

from ucal import ucal_units

####################
# START OF OPTIONS #
####################

# working precision in base-10 decimal units
working_precision_digits = 32

# output precision in base-10 decimal units
output_precision_digits = 16

# if True, will replace non-infix % with (1/100)
allow_percent = True

# if True, will show debug output
debug_output = False

# if True, will verify conversions were done correctly
verify_unit_conversions = True

##################
# END OF OPTIONS #
##################

# define items to be imported with import *
__all__ = ['evaluate', 'ParserError', 'interpret', 'infix_operators',
           'QuantityError', 'unit_def', 'debug_output']


class QuantityError(Exception):
    """
    This is a custom Exception for the Quantity class.

    The arguments should be [title, message, optional_value].

    """
    pass


class ParserError(Exception):
    """This is a custom Exception for the parser module."""
    pass


class Token:
    """The Token class defines various token types."""
    opening_parenthesis = '('
    closing_parenthesis = ')'
    function = 'function'
    variable = 'variable'
    value = 'value'
    infix_operator = 'infix_op'
    prefix_operator = 'prefix_op'
    postfix_operator = 'postfix_op'


class Quantity:
    """A Quantity represents a physical quantity--a number with units."""

    def __init__(self, value=decimal.Decimal(0), units=None):
        """Initialize."""
        self.value = decimal.Decimal(value)
        if units is not None:
            self.units = units
        else:
            self.units = [0.0] * unit_count

    def __str__(self):
        """Convert to a human-readable string."""
        upper_units = []
        for x, y in zip(self.units, base_units):
            if x == int(x):
                x = int(x)
            if x == 0.0:
                continue
            elif x == 1.0:
                upper_units.append(y)
            elif x == -1.0:
                upper_units.append('%s^-1' % y)
            elif x > 0:
                upper_units.append('%s^%s' % (y, x))
            else:
                upper_units.append('%s^%s' % (y, x))
        value_str = '0' if self.value == 0 else str(self.value)
        if 'E' in value_str:
            base, exponent = value_str.split('E')
            exponent = str(int(exponent))
            if '.' in base:
                base = base.rstrip('0').rstrip('.')
            value_str = base + 'e' + exponent
        elif '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        if upper_units:
            return value_str + ' ' + ' '.join(upper_units)
        else:
            return value_str

    def __repr__(self):
        return 'Quantity(' + str(self) + ')'

    def __eq__(self, other):
        if type(other) is Quantity:
            return self.value == other.value and self.units == other.units
        return self.value == other and self.is_unitless()

    def __add__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value + other.value, units=list(self.units))

    def __sub__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value - other.value, units=list(self.units))

    def __mul__(self, other):
        return Quantity(value=self.value * other.value,
                        units=[x + y for x, y in zip(self.units, other.units)])

    def __truediv__(self, other):
        return Quantity(value=self.value / other.value,
                        units=[x - y for x, y in zip(self.units, other.units)])

    def __neg__(self):
        return Quantity(value=-self.value, units=self.units)

    def __pos__(self):
        return Quantity(value=+self.value, units=self.units)

    def __mod__(self, other):
        if self.units != other.units:
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=self.value % other.value,
                        units=[0.0] * unit_count)

    def __pow__(self, other):
        if not other.is_unitless():
            raise QuantityError('Inconsistent units',
                                'Values in the exponent must be unitless.',
                                self)
        return Quantity(value=self.value ** other.value,
                        units=[x * float(other.value) for x in self.units])

    def matches_units(self, other):
        """Return True if this has the same units as the other value."""
        return all(x == y for x, y in zip(self.units, other.units))

    def is_unitless(self):
        """Return True if the value is unitless."""
        return all(x == 0.0 for x in self.units)

    def is_integer(self):
        """Return True if the value is an integer."""
        return (self.is_unitless() and
                self.value == self.value.to_integral_value())

    def factorial(self):
        if not self.is_unitless():
            raise QuantityError('Inconsistent units', self)
        if self.value.to_integral_value() != self.value or self.value < 0:
            raise QuantityError('Invalid value', self)
        new_value = decimal.Decimal('1')
        while self.value > 1:
            new_value *= self.value
            self.value -= 1
        return Quantity(value=new_value,
                        units=[0.0] * unit_count)

    # function are given with the prefix "function_"
    # for example, "sqrt(value)" would call "value.function_sqrt()"
    def function_sqrt(self):
        return Quantity(value=self.value.sqrt(),
                        units=[x / 2.0 for x in self.units])

    def function_exp(self):
        if not self.is_unitless():
            raise QuantityError('Inconsistent units',
                                'Exponent values must be unitless.',
                                self)
        return Quantity(value=self.value.exp(),
                        units=self.units)

    def function_abs(self):
        return Quantity(value=abs(self.value),
                        units=self.units)

    def function_ln(self):
        if not self.is_unitless():
            raise QuantityError('Inconsistent units', self)
        return Quantity(value=self.value.ln(),
                        units=self.units)

    def function_log(self):
        return self.function_ln()

    def function_log10(self):
        if not self.is_unitless():
            raise QuantityError('Inconsistent units', self)
        return Quantity(value=self.value.log10(),
                        units=self.units)

    def function_atan2(self, other):
        if not self.is_unitless():
            raise QuantityError('Inconsistent units', self, other)
        if not other.is_unitless():
            raise QuantityError('Inconsistent units', self, other)
        return Quantity(value=math.atan2(self.value, other.value))


# rules for implicit multiplication
implicit_multiplication_rules = dict()
implicit_multiplication_rules[Token.value] = [Token.variable]
implicit_multiplication_rules[Token.variable] = [Token.variable]
implicit_multiplication_rules[Token.closing_parenthesis] = (
    [Token.variable, Token.opening_parenthesis])

# rules for what token can follow another token
token_can_follow = dict()
token_can_follow[Token.opening_parenthesis] = {Token.function,
                                               Token.variable,
                                               Token.value,
                                               Token.prefix_operator,
                                               Token.opening_parenthesis}
token_can_follow[Token.closing_parenthesis] = {Token.closing_parenthesis,
                                               Token.infix_operator,
                                               Token.postfix_operator,
                                               Token.closing_parenthesis}
token_can_follow[Token.function] = {Token.opening_parenthesis}
token_can_follow[Token.variable] = {Token.closing_parenthesis,
                                    Token.infix_operator,
                                    Token.postfix_operator}
token_can_follow[Token.value] = token_can_follow[Token.variable]
token_can_follow[Token.infix_operator] = {Token.opening_parenthesis,
                                          Token.function,
                                          Token.variable,
                                          Token.value,
                                          Token.prefix_operator}
token_can_follow[Token.prefix_operator] = {Token.opening_parenthesis,
                                           Token.function,
                                           Token.variable,
                                           Token.value}
token_can_follow[Token.postfix_operator] = {Token.closing_parenthesis,
                                            Token.infix_operator}

# allowable tokens at the start of an equation
token_can_start = token_can_follow[Token.infix_operator]

# allowable tokens at the end of an equation
token_can_end = {Token.closing_parenthesis,
                 Token.variable,
                 Token.value,
                 Token.postfix_operator}

# default unit systems
unit_systems = dict()
unit_systems['SI'] = ['kg', 'm', 's', 'A', 'K', 'mol', 'cd', 'byte']

# hold dictionary mapping unit name to a Quantity()
unit_def = dict()

# base unit system
base_units = unit_systems['SI']

# number of base units
unit_count = len(base_units)

# natural units for output
natural_unit = dict()
natural_unit['N'] = 'force'
natural_unit['W'] = 'power'
natural_unit['J'] = 'energy'
natural_unit['m'] = 'length'
natural_unit['kg'] = 'mass'
natural_unit['s'] = 'time'
natural_unit['A'] = 'current'
natural_unit['K'] = 'temperature'
natural_unit['mol'] = 'amount'
natural_unit['cd'] = 'intensity'
natural_unit['m^2'] = 'area'
natural_unit['m^3'] = 'volume'
natural_unit['m/s'] = 'velocity'
natural_unit['m/s^2'] = 'acceleration'
natural_unit['kg/m^3'] = 'density'
natural_unit['Pa'] = 'stress'
natural_unit['V'] = 'electric potential'
natural_unit['F'] = 'capacitance'
natural_unit['Ohm'] = 'electric resistance'
natural_unit['H'] = 'inductance'
natural_unit['Mbps'] = 'data rate'
natural_unit['byte'] = 'data'
natural_unit['Hz'] = 'frequency'

# hold conversion from a Quantity unit tuple to a natural output unit
# natural_unit_map[(1.0, 0.0, ...)] = ('m', 'length', evaluate('m'))
natural_unit_map = dict()

# prefix operators and their corresponding precedence and functions
prefix_operators = dict()
prefix_operators['-'] = (2, Quantity.__neg__)
prefix_operators['+'] = (2, Quantity.__pos__)

# infix operators and their corresponding precedence and functions
infix_operators = dict()
infix_operators['+'] = (4, Quantity.__add__)
infix_operators['-'] = (4, Quantity.__sub__)
infix_operators['/'] = (3, Quantity.__truediv__)
infix_operators['*'] = (3, Quantity.__mul__)
infix_operators['%'] = (3, Quantity.__mod__)
infix_operators['^'] = (1, Quantity.__pow__)

# postfix operators and their corresponding precedence and functions
postfix_operators = dict()
postfix_operators['!'] = (1, Quantity.factorial)

# valid starting characters for variables and functions
starting_variable_characters = string.ascii_letters

# valid following characters for variables and functions
following_variable_characters = string.ascii_letters + string.digits


def find_math_functions():
    """Return math functions defined in this file."""
    global math_functions
    # determine functions and how many arguments each of them take
    # math_functions['sqrt'] -> (Quantity.function_sqrt, arg_count)
    math_functions = dict()
    prefix = 'function_'
    names = inspect.getmembers(Quantity, predicate=inspect.isfunction)
    names = [x for x in names if x[0].startswith(prefix)]
    if debug_output:
        print('Adding %d functions.' % (len(names)))
    for f in names:
        name = f[0][len(prefix):]
        math_functions[name] = (len(inspect.getfullargspec(f[1])[0]), f[1])


def parse_value_at_start(text):
    """Return the string of the value at the start, or None if not found."""
    # parse hexadecimal number
    if len(text) > 2 and text[:2].lower() == '0x':
        i = 2
        while len(text) > i and text[i] in string.hexdigits:
            i += 1
        if i > 2:
            return text[:i]
    # parse binary number
    if len(text) > 2 and text[:2].lower() == '0b':
        i = 2
        while len(text) > i and text[i] in '01':
            i += 1
        if i > 2:
            return text[:i]
    # skip sign if present
    i = 0
    if i >= len(text):
        return None
    if text[i] in '-+':
        i += 1
        if i >= len(text):
            return None
    # get digits before decimal point, if any
    found_digit = False
    while text[i].isdigit():
        found_digit = True
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # skip decimal point if present
    if text[i] == '.':
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # get digits after decimal point if any
    while text[i].isdigit():
        found_digit = True
        i += 1
        if i >= len(text):
            if found_digit:
                return text[:i]
            else:
                return None
    # if no value found so far, we're done
    if not found_digit:
        return None
    # try to parse an exponent
    if text[i].lower() != 'e':
        return text[:i]
    start_index = i
    i += 1
    if i >= len(text):
        return text[:start_index]
    # parse sign if any
    if text[i] in '+-':
        i += 1
        if i >= len(text):
            return text[:start_index]
    # parse digits
    found_digit = False
    while i < len(text) and text[i].isdigit():
        found_digit = True
        i += 1
    if found_digit:
        return text[:i]
    else:
        return text[:start_index]


def parse_variable_at_start(text):
    """Return the string of the variable at the start, or None if not found."""
    if not text or not text[0] in starting_variable_characters:
        return None
    i = 1
    while i < len(text) and text[i] in following_variable_characters:
        i += 1
    return text[:i]


def add_implicit_multiplication(tokens):
    """
    Add implicit multiplication between tokens where necessary.

    implicit parenthesis rules:
    1) between a value and a variable:
       7 mm -> 7 * mm
    2) between a variable and a variable:
       in lbs -> in * lbs
    3) between a closing parenthesis and a variable
       (2 * 12) mm -> (2 * 12) * mm
    4) between parentheses
       (8)(9) -> (8) * (9)

    """
    added_any = False
    i = 0
    rules = implicit_multiplication_rules
    while i < len(tokens) - 1:
        if tokens[i][0] in rules and tokens[i + 1][0] in rules[tokens[i][0]]:
            if debug_output:
                if not added_any:
                    print('Adding implicit parentheses:')
                    added_any = True
            if debug_output:
                print('- adding implicit * between %s and %s'
                      % (tokens[i], tokens[i + 1]))
            tokens.insert(i + 1, ['infix_op', '*'])
        i += 1
    if debug_output:
        if added_any:
            print('- we now have %d tokens' % len(tokens))
            print('  ' + ' '.join(x[1] for x in tokens))
            print('  ' + ' '.join('^' * len(x[1]) for x in tokens))


def parse_to_tokens(equation):
    """Take the equation and parse it into tokens."""
    if debug_output:
        print('\nParsing equation "%s"' % equation)
    # set to true if a value immediately preceded the current character
    parsed_values = []
    while equation:
        # print '-->', equation, parsed_values
        # trim equation if necessary
        if equation and equation[0].isspace():
            equation = equation.lstrip()
            continue
        # see if a value immediately preceeded this position
        if not parsed_values:
            value_before = False
        else:
            if (parsed_values[-1][0] == Token.closing_parenthesis or
                    parsed_values[-1][0] == Token.variable or
                    parsed_values[-1][0] == Token.value or
                    parsed_values[-1][0] == Token.postfix_operator):
                value_before = True
            else:
                value_before = False
        # look for parenthesis
        if equation.startswith('('):
            parsed_values.append([Token.opening_parenthesis, '('])
            equation = equation[1:]
            continue
        if equation.startswith(')'):
            parsed_values.append([Token.closing_parenthesis, ')'])
            equation = equation[1:]
            continue
        # look for prefix operators if value was not immediately preceeding
        if not value_before:
            found_operator = False
            for operator in prefix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.prefix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # look for infix operator if value was preceeding
        if value_before:
            found_operator = False
            for operator in infix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.infix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # look for postfix operator if value was preceeding
        if value_before:
            found_operator = False
            for operator in postfix_operators.keys():
                if equation.startswith(operator):
                    found_operator = True
                    parsed_values.append([Token.postfix_operator,
                                          operator])
                    equation = equation[len(operator):]
                    break
            if found_operator:
                continue
        # try to parse a variable or function
        result = parse_variable_at_start(equation)
        if result is not None:
            equation = equation[len(result):]
            if equation and equation[0] == '(':
                parsed_values.append([Token.function, result])
            else:
                parsed_values.append([Token.variable, result])
            continue
        # try to parse a value
        result = parse_value_at_start(equation)
        if result is not None:
            parsed_values.append([Token.value, result])
            equation = equation[len(result):]
            continue
        # we don't know what to do here
        message = 'Symbol "%s" is not recognized' % equation[0]
        raise ParserError(message, equation)
        # raise ParserError('Unrecognized symbol', equation)
    if debug_output:
        print('- found %d tokens' % (len(parsed_values)))
        print('- ' + ' '.join(x[1] for x in parsed_values))
        print('- ' + ' '.join('^' * len(x[1]) for x in parsed_values))
    return parsed_values


def evaluate_flat_tokens(tokens):
    """Evaluate the given non-parenthesis tokens."""
    if debug_output:
        print('Evaluating tokens ', tokens)
    tokens = list(tokens)
    # ensure no parenthesis are present
    assert not any(x[0] == Token.opening_parenthesis for x in tokens)
    assert not any(x[0] == Token.closing_parenthesis for x in tokens)
    # evaluate functions
    function_indices = [i
                        for i, x in enumerate(tokens)
                        if x[0] == Token.function]
    for i in reversed(function_indices):
        if tokens[i][1] not in math_functions:
            message = 'Function "%s" not recognized' % (tokens[i][1])
            raise ParserError(message)  # 'Unrecognized function', message)
        this_function = math_functions[tokens[i][1]]
        if this_function[0] != 1:
            message = 'Functions with 2+ arguments not supported'
            raise ParserError(message)  # 'Invalid function', message)
        this_value = this_function[1](tokens[i + 1][1])
        del tokens[i + 1]
        tokens[i] = [Token.value, this_value]
    # evaluate exponentiation from right to left
    for i in reversed(range(1, len(tokens))):
        if (tokens[i][0] == Token.infix_operator and
                tokens[i][1][-1] == Quantity.__pow__):
            assert tokens[i - 1][0] == Token.value
            assert tokens[i + 1][0] == Token.value
            tokens[i - 1: i + 2] = [[Token.value,
                                     tokens[i][1][-1](tokens[i - 1][1],
                                                      tokens[i + 1][1])]]
        elif (tokens[i][0] == Token.postfix_operator and
                tokens[i][1][-1] == Quantity.factorial):
            assert tokens[i - 1][0] == Token.value
            tokens[i - 1: i + 1] = [[Token.value,
                                     tokens[i][1][-1](tokens[i - 1][1])]]
    # evaluate everything else left to right
    while len(tokens) > 1:
        # get the lowest order of operations present in the equation and
        # evaluate them
        this_order = min(x[1][0]
                         for x in tokens
                         if (x[0] == Token.infix_operator or
                             x[0] == Token.prefix_operator))
        i = 0
        while i < len(tokens):
            if (tokens[i][0] == Token.prefix_operator and
                    tokens[i][1][0] == this_order):
                assert tokens[i + 1][0] == Token.value
                tokens[i: i + 2] = [[Token.value,
                                     tokens[i][1][-1](tokens[i + 1][1])]]
            elif (tokens[i][0] == Token.infix_operator and
                  tokens[i][1][0] == this_order):
                assert tokens[i - 1][0] == Token.value
                assert tokens[i + 1][0] == Token.value
                tokens[i - 1: i + 2] = [[Token.value,
                                         tokens[i][1][-1](tokens[i - 1][1],
                                                          tokens[i + 1][1])]]
                i -= 1
            i += 1
    # at this point, it should be a single value
    assert len(tokens) == 1
    assert tokens[0][0] == Token.value
    assert type(tokens[0][1]) is Quantity
    return tokens[0][1]


def evaluate_tokens(tokens):
    """Return the result of the given equation as a Quantity."""
    if debug_output:
        print('\nstart of calculate2:')
        for x in tokens:
            print(x)
    # eliminate any parenthesis
    tokens = list(tokens)
    opening_index = []
    found = True
    while found:
        found = False
        # print tokens
        for i, x in enumerate(tokens):
            if x[0] == Token.opening_parenthesis:
                opening_index.append(i)
                found = True
            elif x[1] == Token.closing_parenthesis:
                # eliminate this parenthesis level
                # print 'before ->', tokens
                value = evaluate_flat_tokens(tokens[opening_index[-1] + 1:i])
                tokens[opening_index[-1]:i + 1] = [[Token.value, value]]
                # print 'after ->', tokens
                opening_index = opening_index[:-1]
                break
    value = evaluate_flat_tokens(tokens)
    assert type(value) is Quantity
    return value


def check_token_syntax(tokens):
    """Check the syntax of the tokens and report any error found."""
    if debug_output:
        print('\nChecking token syntax')
    # check for empty token list
    if not tokens:
        raise ParserError('Empty expression')
    # check for balanced parenthesis
    level = 0
    for x in tokens:
        if x[0] == Token.opening_parenthesis:
            level += 1
        if x[0] == Token.closing_parenthesis:
            level -= 1
            if level < 0:
                raise ParserError('Unbalanced parentheses')
    if level != 0:
        raise ParserError('Unbalanced parentheses')
    # check for correct starting token
    if tokens[0][0] not in token_can_start:
        raise ParserError('Invalid starting token "%s"' % (tokens[-1][-1]),
                          tokens[0])
    # check for correct starting token
    if tokens[-1][0] not in token_can_end:
        raise ParserError('Invalid ending token "%s"' % (tokens[-1][-1]),
                          tokens[-1])
    # check for valid token sequence
    for i in range(1, len(tokens)):
        if tokens[i][0] not in token_can_follow[tokens[i - 1][0]]:
            raise ParserError('Invalid syntax')
    if debug_output:
        print('- passed')


def interpret_percent_sign(tokens):
    """
    Interpret the % symbol as a percent sign or as an infix operator.

    """
    # if we don't allow the percent sign, nothing to change
    if not allow_percent:
        return
    # the percent sign is allowed immediately following a number and must be
    # followed by an infix operator, or be the last token
    i = 1
    while i < len(tokens):
        if tokens[i - 1][0] == Token.value and tokens[i][1] == '%':
            if debug_output:
                print(i, tokens)
            if (i == len(tokens) - 1 or
                    (tokens[i + 1][0] == Token.infix_operator or
                     tokens[i + 1][0] == Token.closing_parenthesis)):
                if debug_output:
                    print('Interpreted %% as percent sign at index %d' % i)
                tokens[i][0] = Token.value
                tokens[i][1] = '0.01'
                tokens.insert(i, [Token.infix_operator, '*'])
                if debug_output:
                    print(tokens)
                i += 1
        i += 1


def evaluate_value(text):
    """Evaluate the string value and return a Decimal."""
    if text[:2].lower() == '0x' or text[:2].lower() == '0b':
        return decimal.Decimal(eval(text))
    return decimal.Decimal(text)


def calculate(equation):
    """
    Evaluate the string equation and return the result as a Quantity.

    """
    # store units used by the equation
    units_in_equation = []
    # replace all constants with their actual values
    # tokenize the equation
    tokens = parse_to_tokens(equation)
    # process % as a percent sign or as an infix operator
    interpret_percent_sign(tokens)
    # add implicit multiplication where necessary
    add_implicit_multiplication(tokens)
    # ensure syntax is valid
    check_token_syntax(tokens)
    # replace operators with their function info
    for x in tokens:
        if x[0] == Token.prefix_operator:
            x[1] = prefix_operators[x[1]]
        elif x[0] == Token.infix_operator:
            x[1] = infix_operators[x[1]]
        elif x[0] == Token.postfix_operator:
            x[1] = postfix_operators[x[1]]
    # convert each value to a Quantity
    for x in tokens:
        if x[0] == Token.value:
            x[1] = Quantity(value=evaluate_value(x[1]))
    # replace all variables and units with proper values
    for x in tokens:
        if x[0] == Token.variable:
            # see if it's a unit
            if x[1] in unit_def:
                units_in_equation.append(x[1])
                x[0] = Token.value
                x[1] = unit_def[x[1]]
            else:
                # variable not recognized
                message = 'Variable "%s" is undefined.' % x[1]
                raise ParserError(message, equation)
    return evaluate_tokens(tokens)


def import_units():
    """Read in and convert units from ucal_units."""
    global unit_def
    global natural_unit
    # get the set of units to import
    new_units = dict(ucal_units.units)
    # add base unit definitions
    for i, unit_name in enumerate(base_units):
        unit_def[unit_name] = Quantity(value=decimal.Decimal('1'),
                                       units=[0.0] * unit_count)
        unit_def[unit_name].units[i] = 1.0
    # convert each unit to a Quantity
    while new_units:
        # print units.keys()
        decoded_something = False
        for key in list(new_units.keys()):
            value = new_units[key]
            tokens = parse_to_tokens(value)
            add_implicit_multiplication(tokens)
            # print key, value, tokens
            # check to see if all variables are defined units
            this_units = [x[1] in unit_def
                          for x in tokens
                          if x[0] == Token.variable]
            # if not all units are defined, skip it for now
            if this_units:
                if not all(this_units):
                    continue
            # evaluate it and add this unit definition
            unit_def[key] = calculate(value)
            decoded_something = True
            del new_units[key]
        # if we couldn't decode anything, the remaining units are ill-defined
        if not decoded_something:
            print('ERROR: could not decode all units')
            for x in sorted(new_units.keys()):
                print('* %s: %s' % (x, new_units[x]))
            raise ValueError
    # verify that all unit definitions match units
    if verify_unit_conversions:
        for key, value in unit_def.items():
            left = calculate(key)
            assert left.units == value.units


def create_natural_unit_map():
    """Populate the natural_unit_map variable."""
    global natural_unit_map
    # natural_unit_map[(1.0, 0.0, ...)] = ('m', 'length', evaluate('m'))
    for key in sorted(natural_unit.keys()):
        # get the units of this
        value = calculate(key)
        natural_unit_map[tuple(value.units)] = (key, natural_unit[key], value)


def matching_units(value1, value2):
    """Return True if the units of the two values match."""
    if type(value1) is str:
        value1 = calculate(value1)
    if type(value2) is str:
        value2 = calculate(value2)
    return value1.units == value2.units


def get_measure(quantity):
    """
    Return the measure of the units of the given quantity, or None.

    For example, get_measure('m') should return 'length'.

    """
    check = tuple(quantity.units)
    if check in natural_unit_map:
        return natural_unit_map[check][1]
    return None


def to_string(quantity, output_units=None, include_measure=False):
    """Convert the given Quantity to a string."""
    if debug_output:
        print('Converting "%s" with output_units=%s'
              % (quantity, output_units))
    # round exponents to the nearest 1e-5 to
    # get rid of roundoff errors
    quantity.units = [math.floor(x * 1.0e5 + 0.5) / 1.0e5
                      for x in quantity.units]
    if include_measure:
        measure = get_measure(quantity)
        if measure:
            measure = ' [%s]' % measure
        else:
            measure = ''
    else:
        measure = ''
    # see if the output units match
    if (output_units in unit_def and
            quantity.units == unit_def[output_units].units):
        if debug_output:
            print('- found match in unit definitions')
        quantity.value /= unit_def[output_units].value
        quantity.value *= decimal.Decimal(
            '1.' + '0' * decimal.getcontext().prec)
        value_str = str(quantity.value)
        if '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        return "%s %s%s" % (value_str, output_units, measure)
    elif type(output_units) is str:
        units_quantity = calculate(output_units)
        if matching_units(quantity, units_quantity):
            if debug_output:
                print('- found match to derived output units')
            quantity.value /= units_quantity.value
            quantity.value *= decimal.Decimal(
                '1.' + '0' * decimal.getcontext().prec)
            value_str = str(quantity.value)
            if '.' in value_str:
                value_str = value_str.rstrip('0').rstrip('.')
            return '%s %s%s' % (value_str, output_units, measure)
    # otherwise look for the default units for this type
    key = tuple(quantity.units)
    if key in natural_unit_map:
        if debug_output:
            print('- found match in unit_measure')
        quantity.value /= natural_unit_map[key][2].value
        quantity.value *= decimal.Decimal(
            '1.' + '0' * decimal.getcontext().prec)
        value_str = str(quantity.value)
        if '.' in value_str:
            value_str = value_str.rstrip('0').rstrip('.')
        return "%s %s%s" % (value_str, natural_unit_map[key][0], measure)
    # or output in base SI units
    quantity.value *= decimal.Decimal('1.' + '0' * decimal.getcontext().prec)
    if debug_output:
        print('- no match found, using base units')
    return '%s%s' % (str(quantity), measure)


def interpret(equation):
    """Return the result of the equation which may include unit specifiers."""
    # set high working precision
    decimal.getcontext().prec = working_precision_digits
    # set to True when we find an intepreted result
    interpreted_result = False
    # see if the equation is written in the form "x in y"
    separators = ['to', 'as', 'in']
    result = None
    target_units = None
    for word in separators:
        word = ' ' + word + ' '
        if word not in equation:
            continue
        possible_equation, possible_units = equation.rsplit(word, 1)
        try:
            result = calculate(possible_equation)
            if possible_units.lower() == 'hex':
                if not result.is_integer():
                    return 'only integers can be written as hex'
                result = hex(int(result.value.to_integral_value()))
                result = '0x' + result[2:].upper()
                unit_def['Ans'] = result
                return result
            elif (possible_units.lower() == 'bin' or
                  possible_units.lower() == 'binary'):
                if not result.is_integer():
                    return 'only integers can be written as binary'
                result = bin(int(result.value.to_integral_value()))
                unit_def['Ans'] = result
                return result
            units_check = calculate(possible_units)
            assert result.matches_units(units_check)
            target_units = possible_units
            interpreted_result = True
            break
        except (AssertionError, QuantityError, ParserError):
            pass
    # if we didn't find a result, calculate the entire equation
    if not interpreted_result:
        target_units = None
        result = calculate(equation)
    # save answer as "Ans"
    unit_def['Ans'] = result
    # round results for output
    decimal.getcontext().prec = output_precision_digits
    return to_string(+result, target_units)


def evaluate(equation, units=None):
    """
    Evaluate the equation and return the result in the given units.

    Usage:
    >>> evaluate('5km + 1mi')
    (6609.344, 'm')
    >>> evaluate('5km + 1mi', units='mi')
    (4.10685596118667, 'mi')

    """
    # try to evaluate in the requested units
    if units is not None:
        unit_value = calculate(units)
        value = calculate(equation)
        # if units don't match, raise an error
        if not value.matches_units(unit_value):
            raise ParserError
        result = Quantity(value=value.value / unit_value.value, units=None)
        return to_string(result), units
    # evaluate in any units
    return to_string(+calculate(equation))


find_math_functions()
import_units()
create_natural_unit_map()

if __name__ == "__main__":
    pass
