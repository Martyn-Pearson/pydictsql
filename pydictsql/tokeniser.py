from string import ascii_letters, digits
from enum import Enum, auto
import re

REFERENCE_PAT = re.compile(r"{[^}]*}")
NUMBER_PAT = re.compile(r"-?[0-9]+(\.[-0-9]+)?")
STRING_PAT = re.compile(r"(['\"])[^'\"]*\1")

class TokenType(Enum):
    REFERENCE = -1
    NUMBER = -2
    STRING = -3

    EQUALS = -4
    LT = -5
    GT = -6
    LPAREN = -7
    RPAREN = -8

    SELECT = 1
    FROM = 2
    WHERE = 3
    AND = 4
    OR = 5

    @classmethod
    def get_token(cls, val):
        try:
            # First off, see if we have a valid match to a known keyword
            result = cls[val.upper()]
            if result.value > 0: return result
        except:
            pass

        # Lets see if its a symbol
        for ttype, expected in [(cls.EQUALS, "="), (cls.LT, "<"), (cls.GT, ">"), (cls.LPAREN, "("), (cls.RPAREN, ")")]:
            if val == expected: return ttype

        # Not a valid keyword, so lets see if it is another valid construct
        for ttype, pat in [(cls.REFERENCE, REFERENCE_PAT), (cls.NUMBER, NUMBER_PAT), (cls.STRING, STRING_PAT)]:
            if pat.fullmatch(val): return ttype
        return None

class Tokeniser:
    def __init__(self, sql):
        self.sql = sql
        self.pos = 0

    def _curr_char(self):
        return self.sql[self.pos]

    def tokenise(self):
        self.pos = 0
        while self.pos < len(self.sql):
            token = ""
            curr = self._curr_char()
            if curr.isspace():
                self.pos += 1
            elif curr == "{":
                token = self._consume("}")
            elif curr in "'\"":
                token = self._consume(self.sql[self.pos])
            else:
                token = self._consume()

            if token:
                ttype = TokenType.get_token(token)
                if ttype:
                    yield (ttype, token)
                else:
                    raise ValueError("Invalid token", token)

    def _consume(self, separator = None):
        result = self.sql[self.pos]
        self.pos += 1

        if separator:
            sep_hit = lambda x: x == separator
        else:
            sep_hit = lambda x: x not in ascii_letters + digits + "_"

        while self.pos < len(self.sql) and not sep_hit(self.sql[self.pos]):
            result += self.sql[self.pos]
            self.pos += 1
        if separator and self.pos < len(self.sql) and self.sql[self.pos] == separator:
            result += separator
            self.pos += 1

        return result
