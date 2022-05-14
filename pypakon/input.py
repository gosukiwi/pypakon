from pypakon.parser import ParseError


class Position():
    def __init__(self, col=1, line=1):
        self.col = col
        self.line = line

    def increment_col(self):
        self.col += 1

    def increment_line(self):
        self.col = 1
        self.line += 1

    def __repr__(self):
        return f'line {self.line}, col {self.col}'


class Input():
    """
    Input implementation using a string
    """
    def __init__(self, content):
        self.content = content
        self.position = Position()

    @property
    def is_empty(self):
        return len(self.content) == 0

    def consume(self):
        if self.is_empty:
            raise ParseError(self)

        remaining = self.content[1:]
        new_input = Input(remaining)
        new_input.position.col = self.position.col
        new_input.position.line = self.position.line
        if self.content[0] == '\n':
            new_input.position.increment_line()
        else:
            new_input.position.increment_col()
        return new_input

    def peek(self, amount=1):
        if len(self.content) == 0 or amount > len(self.content):
            raise ParseError(self)

        return self.content[0:amount]

    def __iter__(self):
        for char in self.content:
            yield char

    def skip_one(self, character):
        peeked = self.peek()
        if peeked.lower() != character.lower():
            raise ParseError(self)

        return self.consume()

    def skip_many(self, characters):
        remaining = self
        for c in characters:
            remaining = remaining.skip_one(c)
        return remaining

    def skip_optional(self, character):
        try:
            peeked = self.peek()
        except ParseError:
            return self

        if peeked != character:
            return self

        return self.consume()

    def __repr__(self):
        return self.content

    def __str__(self):
        return self.content
