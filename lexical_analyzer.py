from enum import Enum
import re

from typing import List


class LexemeType(Enum):
    # Static lexemes
    # Keywords
    Dim = 'Dim'
    Print = 'Print'
    Const = 'Const'
    Option = 'Option'
    Explicit = 'Explicit'
    Set = 'Set'
    If = 'If'
    Else = 'Else'
    Sub = 'Sub'
    End = 'End'
    For = 'For'
    Each = 'Each'
    Next = 'Next'
    # Arithmetical operators
    Plus = '+'  # unary and binary versions exist
    Minus = '-'  # unary and binary versions exist
    Multiply = '*'
    Exponent = '^'
    Divide = '/'
    IntegerDivide = '\\'
    Mod = 'Mod'
    # Logical operators
    Not = 'Not'
    And = 'And'
    Or = 'Or'
    Xor = 'Xor'
    AndAlso = 'AndAlso'
    OrElse = 'OrElse'
    # Other operators
    Assign = '='  # assign with arithmetic operators exists
    Semicolon = ';'
    DoubleQuote = '"'
    Dot = '.'
    Comma = ','
    OpeningBracket = '('
    ClosingBracket = ')'
    # Dynamic lexemes
    Identifier = '[a-zA-Z_][a-zA-Z0-9_]*'
    Number = '(0|[1-9][0-9]*)'


class UnknownLexemeException(Exception):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.msg = f'Unknown lexeme at {pos}'


class Lexeme:
    def __init__(self, lexeme_type: LexemeType, lexeme_value: str, offset: int, length: int):
        self.lexeme_type = lexeme_type
        self.lexeme_value = lexeme_value
        self.offset = offset
        self.length = length

    def __str__(self):
        return self.lexeme_value


class LexemeDefinition:
    def __init__(self, lexeme_type: LexemeType):
        self._lexeme_type = lexeme_type
        self._representation = lexeme_type.value

    @property
    def lexeme_type(self):
        return self._lexeme_type

    @property
    def representation(self):
        return self._representation


class StaticLexemeDefinition(LexemeDefinition):
    def __init__(self, lexeme_type: LexemeType, is_keyword: bool = False):
        super().__init__(lexeme_type)
        self.is_keyword = is_keyword


class DynamicLexemeDefinition(LexemeDefinition):
    def __init__(self, lexeme_type: LexemeType):
        super().__init__(lexeme_type)
        self._representation = re.compile(lexeme_type.value)


static_lexeme_definitions: List[StaticLexemeDefinition] = [
    # Keywords
    StaticLexemeDefinition(LexemeType.Dim, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Print, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Const, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Option, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Explicit, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Set, is_keyword=True),
    StaticLexemeDefinition(LexemeType.If, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Else, is_keyword=True),
    StaticLexemeDefinition(LexemeType.For, is_keyword=True),
    StaticLexemeDefinition(LexemeType.Each, is_keyword=True),
    StaticLexemeDefinition(LexemeType.End, is_keyword=True),
    # Arithmetical operators
    StaticLexemeDefinition(LexemeType.Plus),
    StaticLexemeDefinition(LexemeType.Minus),
    StaticLexemeDefinition(LexemeType.Multiply),
    StaticLexemeDefinition(LexemeType.Exponent),
    StaticLexemeDefinition(LexemeType.Divide),
    StaticLexemeDefinition(LexemeType.IntegerDivide),
    StaticLexemeDefinition(LexemeType.Mod),
    # Logical operators
    StaticLexemeDefinition(LexemeType.Not),
    StaticLexemeDefinition(LexemeType.And),
    StaticLexemeDefinition(LexemeType.Or),
    StaticLexemeDefinition(LexemeType.Xor),
    StaticLexemeDefinition(LexemeType.AndAlso),
    StaticLexemeDefinition(LexemeType.OrElse),
    # Other operators
    StaticLexemeDefinition(LexemeType.Assign),
    StaticLexemeDefinition(LexemeType.Semicolon),
    StaticLexemeDefinition(LexemeType.DoubleQuote),
    StaticLexemeDefinition(LexemeType.Dot),
    StaticLexemeDefinition(LexemeType.Comma),
    StaticLexemeDefinition(LexemeType.OpeningBracket),
    StaticLexemeDefinition(LexemeType.ClosingBracket)
]
dynamic_lexeme_definitions: List[DynamicLexemeDefinition] = [
    DynamicLexemeDefinition(LexemeType.Identifier),
    DynamicLexemeDefinition(LexemeType.Number)
]


class LexicalAnalyzer:
    space_chars = [' ', '\n', '\r', '\t']

    def __init__(self, source: str):
        self.source = source
        self.offset = 0
        self._lexemes = []

    @property
    def lexemes(self):
        return self._lexemes

    def parse(self):
        while self.in_bounds():
            self.skip_spaces()
            if not self.in_bounds():
                break

            lexeme = self.process_static_lexeme()
            if not lexeme:
                lexeme = self.process_dynamic_lexeme()

            if not lexeme:
                raise UnknownLexemeException(self.offset)

            self.lexemes.append(lexeme)

    def process_static_lexeme(self):
        for lexeme_def in static_lexeme_definitions:
            rep = lexeme_def.representation
            length = len(rep)

            if self.offset + length > len(self.source) or self.source.find(rep, self.offset,
                                                                           self.offset + length) == -1:
                continue

            if self.offset + length < len(self.source) and lexeme_def.is_keyword:
                next_char: str = self.source[self.offset + length]
                if next_char == '_' or next_char.isalnum():
                    continue

            self.offset += length
            return Lexeme(lexeme_type=lexeme_def.lexeme_type, lexeme_value=lexeme_def.representation,
                          offset=self.offset, length=length)
        return None

    def process_dynamic_lexeme(self):
        for lexeme_def in dynamic_lexeme_definitions:
            m = lexeme_def.representation.search(self.source, self.offset)
            if not m:
                continue

            span = m.span()
            match_length = span[1] - span[0]
            self.offset += match_length
            return Lexeme(lexeme_type=lexeme_def.lexeme_type, lexeme_value=m.group(0),
                          offset=self.offset, length=match_length)
        return None

    def skip_spaces(self):
        while self.in_bounds() and self.source[self.offset] in LexicalAnalyzer.space_chars:
            self.offset += 1

    def in_bounds(self):
        return self.offset < len(self.source)
