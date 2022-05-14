import unittest
from pypakon.input import Input
from pypakon.parser import (many1, optional, many0, either, any_of, literal,
                            list_of, optional_list_of, whitespace,
                            optional_whitespace, padleft, padright, padboth,
                            between, any_but, match_until, ParseError, case,
                            sequentially)


match_a = literal('a')
match_b = literal('b')
match_comma = literal(',')


class TestParser(unittest.TestCase):
    def test_many1__works_with_more(self):
        input = Input('aaab')
        parser = many1(match_a)

        nodes, remaining = parser(input)

        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0], 'a')
        self.assertEqual(nodes[1], 'a')
        self.assertEqual(nodes[2], 'a')
        self.assertEqual(remaining.content, 'b')

    def test_many1__fails_with_zero(self):
        parser = many1(match_a)

        with self.assertRaises(ParseError):
            parser(Input(''))

    def test_optional__zero(self):
        input = Input('')
        parser = optional(match_a)

        node, remaining = parser(input)

        self.assertEqual(node, None)

    def test_optional__one(self):
        input = Input('a')
        parser = optional(match_a)

        node, remaining = parser(input)

        self.assertEqual(node, 'a')

    def test_many0__matches_zero(self):
        input = Input('')
        parser = many0(match_a)

        nodes, remaining = parser(input)

        self.assertEqual(len(nodes), 0)

    def test_many0__matches_once(self):
        input = Input('a')
        parser = many0(match_a)

        nodes, remaining = parser(input)

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0], 'a')

    def test_many0__matches_many(self):
        input = Input('aaa')
        parser = many0(match_a)

        nodes, remaining = parser(input)

        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0], 'a')
        self.assertEqual(nodes[1], 'a')
        self.assertEqual(nodes[2], 'a')

    def test_either__matches_second(self):
        input = Input('b')
        parser = either([match_a, match_b])
        node, remaining = parser(input)

        self.assertEqual(node, 'b')
        self.assertEqual(remaining.content, '')

    def test_either__matches_first(self):
        input = Input('a')
        parser = either([match_a, match_b])
        node, remaining = parser(input)

        self.assertEqual(node, 'a')
        self.assertEqual(remaining.content, '')

    def test_any_of(self):
        input = Input('abc')
        parser = any_of('abc')

        node, remaining = parser(input)

        self.assertEqual(node, 'a')
        self.assertEqual(remaining.content, 'bc')

    def test_any_of__last(self):
        input = Input('cba')
        parser = any_of('abc')

        match, remaining = parser(input)

        self.assertEqual(match, 'c')
        self.assertEqual(remaining.content, 'ba')

    def test_literal(self):
        input = Input('cbazz')
        parser = literal('cba')

        match, remaining = parser(input)

        self.assertEqual(match, 'cba')
        self.assertEqual(remaining.content, 'zz')

    def test_list_of(self):
        input = Input('a,a,a')
        parser = list_of(match_a, match_comma)

        match, remaining = parser(input)

        self.assertEqual(match, ['a', 'a', 'a'])
        self.assertEqual(remaining.content, '')

    def test_list_of__fails_if_empty(self):
        parser = list_of(match_a, match_comma)

        with self.assertRaises(ParseError):
            parser(Input(''))

    def test_optional_list_of(self):
        input = Input('a,a,a')
        parser = optional_list_of(match_a, match_comma)

        match, remaining = parser(input)

        self.assertEqual(match, ['a', 'a', 'a'])
        self.assertEqual(remaining.content, '')

    def test_optional_list_of__works_empty(self):
        input = Input('')
        parser = optional_list_of(match_a, match_comma)

        match, remaining = parser(input)

        self.assertEqual(match, [])
        self.assertEqual(remaining.content, '')

    def test_optional_list_of__works_with_one(self):
        input = Input('a')
        parser = optional_list_of(match_a, match_comma)

        match, remaining = parser(input)

        self.assertEqual(match, ['a'])
        self.assertEqual(remaining.content, '')

    def test_whitespace_parser__works_for_space(self):
        input = Input(' ')

        match, remaining = whitespace(input)

        self.assertEqual(match, ' ')
        self.assertEqual(remaining.content, '')

    def test_whitespace_parser__works_for_tab(self):
        input = Input('\t')

        match, remaining = whitespace(input)

        self.assertEqual(match, '\t')
        self.assertEqual(remaining.content, '')

    def test_whitespace_parser__works_for_newline(self):
        input = Input('\n')

        match, remaining = whitespace(input)

        self.assertEqual(match, '\n')
        self.assertEqual(remaining.content, '')

    def test_whitespace_parser__works_for_cr(self):
        input = Input('\r')

        match, remaining = whitespace(input)

        self.assertEqual(match, '\r')
        self.assertEqual(remaining.content, '')

    def test_optional_whitespace(self):
        input = Input('  yeah')

        match, remaining = optional_whitespace(input)

        self.assertEqual(match, '  ')
        self.assertEqual(remaining.content, 'yeah')

    def test_padleft(self):
        input = Input('  a')
        parser = padleft(match_a)

        match, remaining = parser(input)

        self.assertEqual(match, 'a')
        self.assertEqual(remaining.content, '')

    def test_padright(self):
        input = Input('a  ')
        parser = padright(match_a)

        match, remaining = parser(input)

        self.assertEqual(match, 'a')
        self.assertEqual(remaining.content, '')

    def test_padboth(self):
        input = Input('   a  ')
        parser = padboth(match_a)

        match, remaining = parser(input)

        self.assertEqual(match, 'a')
        self.assertEqual(remaining.content, '')

    def test_between(self):
        input = Input(',a,')
        parser = between(match_a, left=match_comma, right=match_comma)

        match, remaining = parser(input)

        self.assertEqual(match, 'a')
        self.assertEqual(remaining.content, '')

    def test_any_but(self):
        input = Input('a')
        parser = any_but('b')

        match, remaining = parser(input)

        self.assertEqual(match, 'a')
        self.assertEqual(remaining.content, '')

    def test_any_but__fails(self):
        input = Input('a')
        parser = any_but('a')

        with self.assertRaises(ParseError):
            parser(input)

    def test_match_until(self):
        input = Input('abcde.')
        parser = match_until('.')

        match, remaining = parser(input)

        self.assertEqual(match, 'abcde')
        self.assertEqual(remaining.content, '.')

    def test_case(self):
        input = Input('aaab')
        parser_a = many1(match_a)
        parser_b = many1(match_b)

        parser = case([
            ('a', parser_a),
            ('b', parser_b),
        ])
        nodes, remaining = parser(input)

        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0], 'a')
        self.assertEqual(nodes[1], 'a')
        self.assertEqual(nodes[2], 'a')
        self.assertEqual(remaining.content, 'b')

    def test_case__fails(self):
        input = Input('ccc')
        parser_a = many1(match_a)
        parser_b = many1(match_b)
        parser = case([
            ('a', parser_a),
            ('b', parser_b),
        ])

        with self.assertRaises(ParseError) as error:
            parser(input)

        self.assertEqual(error.exception.remaining.content, 'ccc')

    def test_sequentially(self):
        input = Input('abc')
        parser = sequentially([match_a, match_b])

        nodes, remaining = parser(input)

        self.assertEqual(nodes, ['a', 'b'])
        self.assertEqual(remaining.content, 'c')

    def test_parse_error_has_proper_position__same_line(self):
        input = Input('ac')
        parser = sequentially([match_a, match_b])

        with self.assertRaises(ParseError) as error:
            parser(input)

        self.assertIn('line 1, col 2', error.exception.message)

    def test_parse_error_has_proper_position__new_line(self):
        input = Input('a\nac')
        parser_a = sequentially([match_a, literal('\n'), match_a])
        parser_b = sequentially([parser_a, match_b])

        with self.assertRaises(ParseError) as error:
            parser_b(input)

        self.assertIn('line 2, col 2', error.exception.message)
