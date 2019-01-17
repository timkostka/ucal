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
                      % (callable.__name__, ', '.join(arguments)))
        return True

    def test_value_comprehension(self):
        """Test for valid value definitions"""
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
        self.no_exception(ucal.evaluate, '1 m')
        self.no_exception(ucal.evaluate, 'm m')
        self.no_exception(ucal.evaluate, '(1) m')
        self.no_exception(ucal.evaluate, '(1)(1)')


if __name__ == '__main__':
    unittest.main(verbosity=2)
