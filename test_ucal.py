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
        self.assertRaises(ucal.ParserError, ucal.evaluate('1)'))
        self.assertRaises(ucal.ParserError, ucal.evaluate('(1'))
        self.assertRaises(ucal.ParserError, ucal.evaluate('(1))'))
        self.assertRaises(ucal.ParserError, ucal.evaluate('((1)'))
        self.assertRaises(ucal.ParserError, ucal.evaluate(')1('))


if __name__ == '__main__':
    unittest.main()
