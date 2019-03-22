"""
Perform unit tests on ucal.py.

"""

import os
import sys
import unittest

# add parent directory to path to ensure we test the correct ucal
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import ucal
except ModuleNotFoundError:
    print('ERROR: ucal not found in path')
    exit(1)

print('Script is at', os.path.abspath(__file__))
print('Testing ucal at', os.path.abspath(ucal.__file__))

# ensure ucal is loaded from the correct place
ucal_dir = os.path.dirname(os.path.dirname(os.path.abspath(ucal.__file__)))
test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert ucal_dir == test_dir


class TestSyntax(unittest.TestCase):
    """Test for correct detection of various syntax error."""

    def test_string_conversion(self):
        """Test errors when converting to a string."""
        self.assertEqual(str(ucal.evaluate('1/m')), '1 m^-1')
        self.assertEqual(str(ucal.evaluate('m^2')), '1 m^2')
        self.assertEqual(str(ucal.evaluate('m^1.5')), '1 m^1.5')

    def test_invalid_equation(self):
        """Test errors when parsing invalid equations."""
        self.assertRaises(ucal.ParserError, ucal.evaluate, '%1')

    def test_quantity_equality(self):
        """Test Quantity.__eq__ function."""
        self.assertEqual(ucal.ucal.calculate('1m'),
                         ucal.ucal.calculate('1m'))

    def test_quantity_addition(self):
        """Test for proper Quantity.__add__ functionality."""
        x = ucal.ucal.calculate('1m')
        self.assertEqual(str(x + x), '2 m')

    def test_quantity_subtraction(self):
        """Test for proper Quantity.__sub__ functionality."""
        x = ucal.ucal.calculate('1m')
        self.assertEqual(str(x - x), '0 m')

    def test_quantity_addition_error(self):
        """Test for proper Quantity.__add__ error checks."""
        x = ucal.ucal.calculate('1m')
        y = ucal.ucal.calculate('0')
        self.assertRaises(ucal.QuantityError, x.__add__, y)

    def test_quantity_subtraction_error(self):
        """Test for proper Quantity.__sub__ error checks."""
        x = ucal.ucal.calculate('1m')
        y = ucal.ucal.calculate('0')
        self.assertRaises(ucal.QuantityError, x.__sub__, y)

    def test_invalid_values(self):
        """Test errors when parsing invalid values."""
        self.assertRaises(ucal.ParserError, ucal.evaluate, '')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '+++1')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '+')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '.')
        self.assertRaises(ucal.ParserError, ucal.evaluate, 'e10')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1ee10')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1E+-1')

    def test_basic_value_comprehension(self):
        """Test for valid value definitions."""
        self.assertEqual(ucal.evaluate('1'), '1')
        self.assertEqual(ucal.evaluate('123457890'), '123457890')
        self.assertEqual(ucal.evaluate('001'), '1')
        self.assertEqual(ucal.evaluate('.1'), '0.1')
        self.assertEqual(ucal.evaluate('+1'), '1')
        self.assertEqual(ucal.evaluate('-1'), '-1')
        self.assertEqual(ucal.evaluate('1e3'), '1000')

    def test_nested_prefix_comprehension(self):
        """Test for valid value definitions."""
        self.assertEqual(ucal.evaluate('1+-2'), '-1')

    def test_output_number_formatting(self):
        """Test for desired output format for numbers."""
        self.assertEqual(ucal.evaluate('0.1234567890'), '0.123456789')
        self.assertEqual(ucal.evaluate('1e9'), '1000000000')
        self.assertEqual(ucal.evaluate('+1e+9'), '1000000000')
        self.assertEqual(ucal.evaluate('-1e-3'), '-0.001')
        self.assertEqual(ucal.evaluate('1E6'), '1000000')

    def test_arithmetic(self):
        """Test basic arithmetic operations."""
        self.assertEqual(ucal.evaluate('1+2'), '3')
        self.assertEqual(ucal.evaluate('1-2'), '-1')
        self.assertEqual(ucal.evaluate('3*4'), '12')
        self.assertEqual(ucal.evaluate('8/2'), '4')
        self.assertEqual(ucal.evaluate('--1'), '1')

    def test_decimal_comprehension(self):
        """Test decimal number comprehension."""
        self.assertEqual(ucal.evaluate('0'), '0')
        self.assertEqual(ucal.evaluate('0123'), '123')
        self.assertEqual(ucal.evaluate('+1e555'), '1e555')
        self.assertEqual(ucal.evaluate('1e-67'), '1e-67')

    def test_binary_comprehension(self):
        """Test binary number comprehension."""
        self.assertEqual(ucal.evaluate('0B0'), '0')
        self.assertEqual(ucal.evaluate('0b0'), '0')
        self.assertEqual(ucal.evaluate('0b11'), '3')
        self.assertEqual(ucal.evaluate('0b1111'), '15')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '0b')

    def test_hexadecimal_comprehension(self):
        """Test hexadecimal number comprehension."""
        self.assertEqual(ucal.evaluate('0x0'), '0')
        self.assertEqual(ucal.evaluate('0X0'), '0')
        self.assertEqual(ucal.evaluate('0x123'), '291')
        self.assertEqual(ucal.evaluate('0xAbCdEf'), '11259375')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '0x')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '0xAG')

    def test_hexadecimal_errors(self):
        """Test hexadecimal number error detection."""
        self.assertIn('only integers', ucal.interpret('1m in hex'))

    def test_binary_errors(self):
        """Test binary number error detection."""
        self.assertIn('only integers', ucal.interpret('1m in bin'))

    def test_hexadecimal_conversion(self):
        """Test conversion to hexademical numbers."""
        self.assertEqual(ucal.interpret('67 in hex'), '0x43')
        self.assertEqual(ucal.interpret('123 in hex'), '0x7B')

    def test_binary_conversion(self):
        """Test conversion to hexademical numbers."""
        self.assertEqual(ucal.interpret('67 in bin'), '0b1000011')

    def test_output_units(self):
        """Test automatic output conversions."""
        self.assertEqual(ucal.evaluate('1A*Ohm'), '1 V')
        self.assertEqual(ucal.evaluate('1/s'), '1 Hz')

    def test_target_simple_units(self):
        """Test conversion to specified units."""
        self.assertEqual(ucal.interpret('1m to mm'), '1000 mm')
        self.assertEqual(ucal.interpret('1m as mm'), '1000 mm')
        self.assertEqual(ucal.interpret('1m in mm'), '1000 mm')

    def test_target_compound_units(self):
        """Test conversion to specified units."""
        self.assertEqual(ucal.interpret('1in^2 to mm^2'), '645.16 mm^2')

    def test_target_units_fallback(self):
        """Test fallback conversion if target units are invalid."""
        self.assertEqual(ucal.interpret('1 in kg'), '0.0254 kg m')

    def test_factorial(self):
        """Test the factorial postfix operator."""
        self.assertEqual(ucal.evaluate('0!'), '1')
        self.assertEqual(ucal.evaluate('1!'), '1')
        self.assertEqual(ucal.evaluate('2!'), '2')
        self.assertEqual(ucal.evaluate('5!'), '120')
        self.assertEqual(ucal.evaluate('18!'), '6402373705728000')

    def test_factorial_error(self):
        """Test invalid uses of the factorial postfix operator."""
        self.assertRaises(ucal.QuantityError, ucal.evaluate, '(1m)!')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, '1.5!')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, '(-1)!')

    def test_percent(self):
        """Test percentage evaluation."""
        self.assertEqual(ucal.evaluate('100%'), '1')
        self.assertEqual(ucal.evaluate('50%'), '0.5')
        self.assertEqual(ucal.evaluate('25%'), '0.25')

    def test_unbalanced_parentheses(self):
        """Test for unbalanced parentheses."""
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1)')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '(1')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '(1))')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '((1)')
        self.assertRaises(ucal.ParserError, ucal.evaluate, ')1(')

    def test_balanced_parentheses(self):
        """Test for balanced parentheses."""
        self.assertEqual(ucal.evaluate('(1)'), '1')
        self.assertEqual(ucal.evaluate('((1))'), '1')
        self.assertEqual(ucal.evaluate('(((((1)))))'), '1')

    def test_invalid_implicit_multiplication(self):
        """Test invalid implicit multiplication."""
        # implicit multiplication not allowed between two values
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1 2')
        # not allowed between left variable and right value
        self.assertRaises(ucal.ParserError, ucal.evaluate, 'm 1')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1 m 1')

    def test_implicit_multiplication(self):
        """Test for valid implicit multiplication."""
        self.assertEqual(ucal.evaluate('1 m'), '1 m')
        self.assertEqual(ucal.evaluate('m m'), '1 m^2')
        self.assertEqual(ucal.evaluate('(1) m'), '1 m')
        self.assertEqual(ucal.evaluate('(1)(1)'), '1')

    def test_power_evaluation_order(self):
        """Test order of power evaluation."""
        self.assertEqual(ucal.evaluate('3^3^3'), '7625597484987')

    def test_evaluation_order_2(self):
        """Test order of power/factorial evaluations."""
        self.assertEqual(ucal.evaluate('3^2!'), '9')

    def test_unrecognized_function(self):
        """Test for an unrecognized function function."""
        self.assertRaises(ucal.ParserError,
                          ucal.evaluate,
                          'thisIsUnrecognized(1)')

    def test_function_sqrt(self):
        """Test sqrt function."""
        self.assertEqual(ucal.evaluate('sqrt(4)'), '2')

    def test_function_exp(self):
        """Test exp function."""
        self.assertEqual(ucal.evaluate('exp(0)'), '1')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, 'exp(1m)')

    def test_function_abs(self):
        """Test abs function."""
        self.assertEqual(ucal.evaluate('abs(1)'), '1')
        self.assertEqual(ucal.evaluate('abs(-1)'), '1')
        self.assertEqual(ucal.evaluate('abs(0)'), '0')
        self.assertEqual(ucal.evaluate('abs(1 m)'), '1 m')

    def test_function_ln(self):
        """Test ln function."""
        self.assertEqual(ucal.evaluate('ln(exp(1))'), '1')
        self.assertEqual(ucal.evaluate('ln(1)'), '0')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, 'ln(1m)')

    def test_function_log(self):
        """Test log function."""
        self.assertEqual(ucal.evaluate('log(exp(1))'), '1')
        self.assertEqual(ucal.evaluate('log(1)'), '0')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, 'log(1m)')

    def test_function_log10(self):
        """Test log10 function."""
        self.assertEqual(ucal.evaluate('log10(1)'), '0')
        self.assertEqual(ucal.evaluate('log10(10)'), '1')
        self.assertEqual(ucal.evaluate('log10(100)'), '2')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, 'log10(1m)')

    def test_mod(self):
        """Test __mod__ function."""
        self.assertEqual(ucal.evaluate('1 % 7'), '1')
        self.assertEqual(ucal.evaluate('7 % 1'), '0')
        self.assertEqual(ucal.evaluate('4 % 2.5'), '1.5')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, '(1m) % 2')

    def test_pow(self):
        """Test __pow__ function."""
        self.assertEqual(ucal.evaluate('1 ^ 7'), '1')
        self.assertEqual(ucal.evaluate('2 ^ 5'), '32')
        self.assertRaises(ucal.QuantityError, ucal.evaluate, '1 ^ (1m)')


if __name__ == '__main__':
    unittest.main()
