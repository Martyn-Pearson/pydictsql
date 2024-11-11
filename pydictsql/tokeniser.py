from collections import namedtuple
from enum import Enum
import re
from string import ascii_letters, digits
import typing

from pydictsql.exceptions import InvalidTokenError, UnexpectedTokenError

REFERENCE_PAT = re.compile(r"{[^}]*}")
NUMBER_PAT = re.compile(r"-?[0-9]+(\.[-0-9]+)?")
STRING_PAT = re.compile(r"(['\"])[^'\"]*\1")
SYMBOLS = "=<>(),*"

_Token = namedtuple("Token", ["ttype", "value"])


class _TokenType(Enum):
    REFERENCE = -1
    NUMBER = -2
    STRING = -3

    EQUALS = -4
    LT = -5
    LTE = -6
    GT = -7
    GTE = -8
    NE = -9
    LPAREN = -7
    RPAREN = -8
    COMMA = -9
    ASTERISK = -10

    SELECT = 1
    FROM = 2
    WHERE = 3
    AND = 4
    OR = 5
    NOT = 6

    @classmethod
    def get_token(cls, val):
        try:
            # First off, see if we have a valid match to a known keyword
            result = cls[val.upper()]
            if result.value > 0:
                return result
        except:
            pass

        # Lets see if its a symbol
        for ttype, expected in [
            (cls.EQUALS, "="),
            (cls.LT, "<"),
            (cls.LTE, "<="),
            (cls.GT, ">"),
            (cls.GTE, ">="),
            (cls.NE, "<>"),
            (cls.LPAREN, "("),
            (cls.RPAREN, ")"),
            (cls.COMMA, ","),
            (cls.ASTERISK, "*"),
        ]:
            if val == expected:
                return ttype

        # Not a valid keyword, so lets see if it is another valid construct
        for ttype, pat in [
            (cls.REFERENCE, REFERENCE_PAT),
            (cls.NUMBER, NUMBER_PAT),
            (cls.STRING, STRING_PAT),
        ]:
            if pat.fullmatch(val):
                return ttype

        # Unable to recognise token type
        return None

    @classmethod
    def comparators(cls):
        return set([cls.LT, cls.LTE, cls.GT, cls.GTE, cls.EQUALS, cls.NE])

    @classmethod
    def rvalues(cls):
        return set([cls.REFERENCE, cls.STRING, cls.NUMBER])


class _Tokeniser:
    """
    Constructs a tokeniser, which tokenises the given SQL string
    :param sql: SQL string to be tokenised
    :raises InvalidTokenError: Raised if an unrecognised token is read (for example, an invalid keyword)
    """

    def __init__(self, sql: str):
        self._sql = sql
        self._pos = 0  # Use this for tokenising to start with
        self._tokens = [
            t for t in self._tokenise()
        ]  # Note that we tokenise up front rather than using the generator directly to support look ahead
        self._pos = 0  # Then reuse for managing the consumption of tokens

    """
    Consume and return a Token, either simply returning the Token or validating that it is of the expected type. If not, a ValueError is raised
    :param expected: TokenType or set of TokenTypes that we expect to consume
    :returns: Token if present (and matches expected, if given), otherwise None
    :raises ValueError: Raised if consumed token does not match expected type
    """

    def consume(self, expected: typing.Optional[typing.Union[_TokenType, set]] = None):
        if expected and isinstance(expected, _TokenType):
            expected = set([expected])
        if self._pos < len(self._tokens):
            token = self._tokens[self._pos]
            if expected and token.ttype not in expected:
                raise UnexpectedTokenError(token, expected)
            self._pos += 1
            return token
        elif expected:
            raise UnexpectedTokenError(None, expected)
        return None

    """
    Return the next Token without consuming it, so that the parser can determine the appropriate action
    :returns: Next Token that will be consumed
    """

    def peek_next(self):
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    """
    Returns whether the next token is of a given type. Like peek_next, does not consume the token
    :returns: True if next token is of the type specified, False otherwise (including if there is no next token)
    """

    def next_is(self, ttype: _TokenType):
        next = self.peek_next()
        return next and next.ttype == ttype

    def _curr_char(self):
        return self._sql[self._pos]

    def _tokenise(self):
        self._pos = 0
        while self._pos < len(self._sql):
            token = ""
            curr = self._curr_char()
            if curr.isspace():
                self._pos += 1
            elif curr == "{":
                # This is a reference, so collect up to and including the closing brace
                token = self._collect("}")
            elif curr in "'\"":
                # This is a string, so collect up to and including the closing matching quote
                token = self._collect(self._sql[self._pos])
            elif curr in SYMBOLS:
                # This is an operator - either a single character or compound comparator, collect the whole operator
                token = self._collect_operator()
            else:
                # Probably a keyword, collect until we hit a separator
                token = self._collect()

            if token:
                ttype = _TokenType.get_token(token)
                if ttype:
                    yield _Token(ttype, token)
                else:
                    raise InvalidTokenError(token)

    def _collect(self, separator=None):
        result = self._sql[self._pos]
        self._pos += 1

        if separator:
            sep_hit = lambda x: x == separator
        else:
            sep_hit = lambda x: x not in ascii_letters + digits + "_."

        while self._pos < len(self._sql) and not sep_hit(self._sql[self._pos]):
            result += self._sql[self._pos]
            self._pos += 1
        if (
            separator
            and self._pos < len(self._sql)
            and self._sql[self._pos] == separator
        ):
            result += separator
            self._pos += 1

        return result

    def _collect_operator(self):
        check = self._sql[self._pos : self._pos + 2]
        if check in [">=", "<=", "<>"]:
            self._pos += 2
            return check
        curr = self._curr_char()
        self._pos += 1
        return curr
