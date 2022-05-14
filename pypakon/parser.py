class ParseError(Exception):
    def __init__(self, remaining):
        message = f'Syntax error at {remaining.position}'
        super().__init__(message)
        self.remaining = remaining
        self.message = message


def optional(parser):
    """
    Tries to match a parser. Returns a null node if the parser raises
    ParseError.
    """
    def wrapper(remaining):
        try:
            return parser(remaining)
        except ParseError:
            return None, remaining

    return wrapper


def many1(parser):
    """
    Matches a parser until it raises ParseError. It raises ParseError if
    it matches zero times.
    """
    def wrapper(remaining):
        nodes = []
        try:
            while True:
                node, remaining = parser(remaining)
                nodes.append(node)
        except ParseError:
            if len(nodes) == 0:
                raise ParseError(remaining)
            else:
                return (nodes, remaining)

    return wrapper


def many0(parser):
    """
    Matches a parser until it raises ParseError. It returns an empty array
    if it matches zero times.
    """
    def wrapper(remaining):
        try:
            return many1(parser)(remaining)
        except ParseError:
            return [], remaining

    return wrapper


def either(parsers):
    def wrapper(remaining):
        for parser in parsers:
            try:
                return parser(remaining)
            except ParseError:
                continue

        raise ParseError(remaining)

    return wrapper


def case(case_list):
    """
    The `case` combinator can pick up the appropritate parser based on a
    look-ahead.

    Because parser combinators can backtrack a lot, they can be slow if left
    unmanaged. Manually selecting the correct parser based on a look-ahead
    instead of trying every single parser speeds things up considerably.

    When making `or` branches in your parsers, try to use this approach
    whenever possible.

    Usage:

        my_parser = case([
            ('a', a_very_slow_parser),
            ('bc', another_slowpoke),
        ])

    NOTE: The above is not a particularly good example, but assuming both
    parsers are composed of several smaller parsers, peeking a single char can
    significantly reduce the amount of parsers ran.
    """
    def wrapper(remaining):
        for startswith, parser in case_list:
            if remaining.peek(len(startswith)) == startswith:
                return parser(remaining)

        raise ParseError(remaining)

    return wrapper


def sequentially(parsers):
    def wrapper(remaining):
        nodes = []
        for parser in parsers:
            node, remaining = parser(remaining)
            nodes.append(node)
        return nodes, remaining

    return wrapper


def literal(string):
    def wrapper(remaining):
        return string, remaining.skip_many(string)

    return wrapper


def any_of(characters):
    def wrapper(remaining):
        for c in characters:
            try:
                match = c
                remaining = remaining.skip_one(c)
                return match, remaining
            except ParseError:
                continue

        raise ParseError(remaining)

    return wrapper


def any_but(characters):
    """matches any character except the ones given"""
    def wrapper(remaining):
        character = remaining.peek()
        if character in characters:
            raise ParseError(remaining)
        else:
            remaining = remaining.consume()
            return character, remaining

    return wrapper


def match_until(characters):
    """matches until any of the given characters is found"""
    return join(many1(any_but(characters)))


def list_of(parser, separator):
    def wrapper(remaining):
        single, remaining = parser(remaining)
        try:
            _, remaining = separator(remaining)
        except ParseError:
            return ([single], remaining)

        list, remaining = wrapper(remaining)
        return ([single] + list, remaining)

    return wrapper


def optional_list_of(parser, separator):
    def wrapper(remaining):
        try:
            single, remaining = parser(remaining)
        except ParseError:
            return ([], remaining)

        try:
            _, remaining = separator(remaining)
        except ParseError:
            return ([single], remaining)

        list, remaining = wrapper(remaining)
        return ([single] + list, remaining)

    return wrapper


def padleft(parser, padding=None):
    padding = optional_whitespace if padding is None else padding

    def wrapper(remaining):
        _, remaining = padding(remaining)
        return parser(remaining)

    return wrapper


def padright(parser, padding=None):
    padding = optional_whitespace if padding is None else padding

    def wrapper(remaining):
        match, remaining = parser(remaining)
        _, remaining = padding(remaining)
        return match, remaining

    return wrapper


def padboth(parser, padding=None):
    padding = optional_whitespace if padding is None else padding

    def wrapper(remaining):
        _, remaining = padding(remaining)
        match, remaining = parser(remaining)
        _, remaining = padding(remaining)
        return match, remaining

    return wrapper


def join(parser):
    def wrapper(remaining):
        value, remaining = parser(remaining)
        value = ''.join(value)
        return value, remaining

    return wrapper


def between(parser, left, right):
    def wrapper(remaining):
        _, remaining = left(remaining)
        value, remaining = parser(remaining)
        _, remaining = right(remaining)
        return value, remaining

    return wrapper


# base parsers
space = any_of(' \t\r')
whitespace = any_of(' \n\t\r')
optional_whitespace = join(many0(whitespace))
optional_space = join(many0(space))
