"""
Perform unit tests on ucal.py.

"""


import unittest

import ucal


class TestSyntax(unittest.TestCase):
    """Test for correct detection of various syntax error."""

    def no_exception(self, function, *args, **kwargs):
        """Return True if no exceptions are raised, else False."""
        passed = True
        try:
            function(*args, **kwargs)
        except ucal.ParserError:
            passed = False
        if not passed:
            arguments = [*args]
            arguments.extend('%s=%s' % (x, y) for x, y in kwargs.items())
            self.fail('%s(%s) raised an exception.'
                      % (function.__name__, ', '.join(arguments)))
        return True

    def test_value_comprehension(self):
        """Test for valid value definitions."""
        self.no_exception(ucal.evaluate, '1')
        self.no_exception(ucal.evaluate, '123457890')
        self.no_exception(ucal.evaluate, '001')
        self.no_exception(ucal.evaluate, '0.1234567890')
        self.no_exception(ucal.evaluate, '.1')
        self.no_exception(ucal.evaluate, '+1')
        self.no_exception(ucal.evaluate, '-1')
        self.no_exception(ucal.evaluate, '1e9')
        self.no_exception(ucal.evaluate, '+1e+9')
        self.no_exception(ucal.evaluate, '-1e-9')
        self.no_exception(ucal.evaluate, '1E6')

    def test_arithmetic(self):
        """Test basic arithmetic operations."""
        self.assertEqual(ucal.evaluate('1+2'), '3')
        self.assertEqual(ucal.evaluate('1-2'), '-1')
        self.assertEqual(ucal.evaluate('3*4'), '12')
        self.assertEqual(ucal.evaluate('8/2'), '4')

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
        self.no_exception(ucal.evaluate, '1 m')
        self.no_exception(ucal.evaluate, 'm m')
        self.no_exception(ucal.evaluate, '(1) m')
        self.no_exception(ucal.evaluate, '(1)(1)')

    def test_power_evaluation_order(self):
        """Test order of power evaluation."""
        self.assertEqual(ucal.evaluate('3^3^3'), '7625597484987')

    def test_evaluation_order_2(self):
        """Test order of power/factorial evaluations."""
        self.assertEqual(ucal.evaluate('3^2!'), '9')


if __name__ == '__main__':
    unittest.main()
