# Pypakon
A simply Python Parser Combinator library.

# Parsers 101
A parser takes some input, and returns whether the input matches a given
pattern or not. You can think of them as regular expressions on steroids.

A parser combinator takes two or more parsers, and _combines_ them together
into a new parser.

For example, if you have a parser `match_a` which matches the letter a, you
can use the `many1` combinator to match it 1 or more times. So it will match
`a`, `aa`, `aaa` and so on.

```python
from pypakon.parsers import many1, literal
from pypakon.input import Input

match_a = literal('a')
match_as = many1(match_a)

result, remaining = match_as(Input('aaaab'))
# result is ['a', 'a', 'a', 'a']
# remaining is Input('b')
```

A `ParseError` is raised if the parser can't match the given input. It will
report the position at which the error happened.

```python
try:
  my_parser(input)
except ParseError as error:
  print(error)
  # the error already includes the position, you can access it manually if you
  # want:
  # position = error.remaining.position
```

Pypakon provides the following combinators: 
* `any_but`
* `any_of`
* `between`
* `case`
* `either`
* `join`
* `list_of`
* `literal`
* `many0`
* `many1`
* `match_until`
* `optional_list_of`
* `optional`
* `padboth`
* `padleft`
* `padright`
* `sequentially`

Pypakon also provides the following convenience parsers:

* `space`: Matches a space, tab or `\r`
* `whitespace`: Matches a `space` or a new line
* `optional_space`: Matches an optional space
* `optional_whitespace`: Matches an optional whitespace

# TODO
Implement: 
* `exactly`: Matches a parser a certain amount of times
* Do not force case insensitivity
