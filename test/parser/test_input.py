import unittest
from pypakon.input import Input
from pypakon.parser import ParseError


class TestInput(unittest.TestCase):
    def test_consumes_one(self):
        input = Input('foo')

        remaining = input.consume()

        self.assertEqual(remaining.content, 'oo')

    def test_consumes_raises_no_more_input(self):
        with self.assertRaises(ParseError):
            Input('').consume()

    def test_peeks_one(self):
        input = Input('foo')

        peeked = input.peek()

        self.assertEqual(peeked, 'f')

    def test_peeks_many(self):
        input = Input('foo')

        peeked = input.peek(3)

        self.assertEqual(peeked, 'foo')

    def test_peeks_raise_no_more_input(self):
        with self.assertRaises(ParseError):
            Input('foo').peek(4)

    def test_peeks_raise_no_initial_input(self):
        with self.assertRaises(ParseError):
            Input('').peek()

    # skip
    def test_skip_one(self):
        input = Input('foo')

        remaining = input.skip_one('f')

        self.assertEqual(remaining.content, 'oo')

    def test_skip_one__complains(self):
        with self.assertRaises(ParseError):
            Input('foo').skip_one('z')

    def test_skip_optional(self):
        input = Input('foo')

        remaining = input.skip_optional('f')

        self.assertEqual(remaining.content, 'oo')

    def test_skip_optional_ignores(self):
        input = Input('foo')

        remaining = input.skip_optional('g')

        self.assertEqual(remaining.content, 'foo')

    def test_counts_position(self):
        remaining = Input('foo')

        remaining = remaining.skip_many('foo')

        self.assertEqual(remaining.position.line, 1)
        self.assertEqual(remaining.position.col, 4)

    def test_counts_position_lines(self):
        remaining = Input('foo\nba')

        remaining = remaining.skip_many('foo\nba')

        self.assertEqual(remaining.position.line, 2)
        self.assertEqual(remaining.position.col, 3)

    def test_repr(self):
        remaining = Input('foo')

        self.assertEqual(remaining.__repr__(), 'foo')

    def test_iter(self):
        chars = []
        for c in Input('foo'):
            chars.append(c)

        self.assertEqual(chars[0], 'f')
        self.assertEqual(chars[1], 'o')
        self.assertEqual(chars[2], 'o')

    def test_str(self):
        self.assertEqual(Input('foo').__str__(), 'foo')
