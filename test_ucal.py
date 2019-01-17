"""
Perform unit tests on ucal.py.

"""


import unittest

from ucal import evaluate, ParserError
import ucal


class TestSyntax(unittest.TestCase):
    """Test for correct detection of various syntax error."""

    def test_unbalanced_parentheses(self):
        """Test for unbalanced parentheses."""
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1)')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '(1')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '(1))')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '((1)')
        self.assertRaises(ucal.ParserError, ucal.evaluate, ')1(')

    def test_invalid_implicit_multiplication(self):
        """Test invalid implicit multiplication."""
        # implicit multiplication not allowed between two values
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1 2')
        # not allowed between left variable and right value
        self.assertRaises(ucal.ParserError, ucal.evaluate, 'm 1')
        self.assertRaises(ucal.ParserError, ucal.evaluate, '1 m 1')

    def test_implicit_multiplication(self):
        """Test for valid implicit multiplication."""
        ucal.evaluate('1 m')
        ucal.evaluate('m m')
        ucal.evaluate('(1) m')
        ucal.evaluate('(1)(1)')


if __name__ == '__main__':
    unittest.main()
